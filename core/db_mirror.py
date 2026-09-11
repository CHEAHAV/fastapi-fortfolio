from typing import Any
import logging
from functools import lru_cache

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from config import settings

logger = logging.getLogger(__name__)


def _mirror_database_url() -> str:
    if settings.DATABASE_URL == settings.LOCAL_DATABASE_URL and settings.NEON_DATABASE_URL:
        return settings.NEON_DATABASE_URL

    if settings.DATABASE_URL == settings.NEON_DATABASE_URL and settings.LOCAL_DATABASE_URL:
        return settings.LOCAL_DATABASE_URL

    return ""


def _row_data(instance: Any) -> dict[str, Any]:
    mapper = inspect(instance).mapper
    return {
        column.key: getattr(instance, column.key)
        for column in mapper.column_attrs
    }


def _primary_key_filter(instance: Any) -> dict[str, Any]:
    mapper = inspect(instance).mapper
    return {
        column.key: getattr(instance, column.key)
        for column in mapper.primary_key
    }


class MirroringSession(Session):
    def commit(self) -> None:
        mirror_url = _mirror_database_url()
        should_mirror = settings.MIRROR_DATABASE_WRITES and bool(mirror_url)

        upserts = []
        deletes = []
        if should_mirror:
            changed = list(self.new) + list(self.dirty)
            deleted = list(self.deleted)
            # Materialize generated IDs/defaults before copying values to Neon.
            # Flush clears new/dirty collections, so retain the instances first.
            self.flush()
            upserts = [
                (type(instance), _row_data(instance))
                for instance in changed
                if inspect(instance, raiseerr=False) is not None
            ]
            deletes = [
                (type(instance), _primary_key_filter(instance))
                for instance in deleted
                if inspect(instance, raiseerr=False) is not None
            ]

        super().commit()

        if should_mirror and (upserts or deletes):
            try:
                _mirror_changes(mirror_url, upserts, deletes)
            except Exception as exc:
                logger.warning("Database mirror write failed: %s", exc)


@lru_cache(maxsize=2)
def _mirror_engine(mirror_url: str):
    return create_engine(
        mirror_url,
        pool_timeout  = 10,
        pool_pre_ping = True,
        connect_args  = {"connect_timeout": 8},
    )


def _mirror_changes(mirror_url: str, upserts: list[tuple[type, dict]], deletes: list[tuple[type, dict]]) -> None:
    mirror_session_factory = sessionmaker(
        autocommit = False,
        autoflush  = False,
        bind       = _mirror_engine(mirror_url),
    )
    mirror_session = mirror_session_factory()

    try:
        for model, values in upserts:
            mirror_session.merge(model(**values))

        for model, key_values in deletes:
            item = mirror_session.get(model, tuple(key_values.values()) if len(key_values) > 1 else next(iter(key_values.values())))
            if item is not None:
                mirror_session.delete(item)

        mirror_session.commit()
    except Exception:
        mirror_session.rollback()
        raise
    finally:
        mirror_session.close()
