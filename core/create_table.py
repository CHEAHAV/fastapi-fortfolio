from core.runtime import require_project_venv
from typing import Any, Mapping
from passlib.context import CryptContext
from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, Text, create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateColumn
from config import settings
from core.api.role.models import TBL_ROLE
from core.api.user.models import TBL_USER
from core.api.module.models import TBL_MODULE
from core.api.sub_module.models import TBL_SUB_MODULE
from core.db import Base
from core.module_loader import import_registered_module_models

require_project_venv()
DEFAULT_ROLE_ID = "SUPERUSER"
DEFAULT_USER_ID = "SUPERUSER"
DEFAULT_USERNAME = "SuperUser"
DEFAULT_PASSWORD = "1qaz!QAZ"
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _quote(active_engine, name: str) -> str:
    return active_engine.dialect.identifier_preparer.quote(name)


def _column_type_sql(active_engine, column) -> str:
    return column.type.compile(dialect=active_engine.dialect)


def _safe_column_definition(active_engine, column) -> str:
    definition = str(CreateColumn(column).compile(dialect=active_engine.dialect))
    if not column.primary_key:
        definition = definition.replace(" NOT NULL", "")
    return definition


def _normalized_type(value: str) -> str:
    return " ".join(value.upper().replace("CHARACTER VARYING", "VARCHAR").split())


def _should_alter_type(active_engine, model_column, database_column: Mapping[str, Any]) -> bool:
    model_type    = model_column.type
    database_type = database_column["type"]

    if isinstance(model_type, String):
        return getattr(database_type, "length", None) != getattr(model_type, "length", None)

    if isinstance(model_type, Numeric):
        return (
            getattr(database_type, "precision", None) != getattr(model_type, "precision", None)
            or getattr(database_type, "scale", None) != getattr(model_type, "scale", None)
        )

    simple_type_pairs = (
        (Boolean, "BOOLEAN"),
        (Integer, "INTEGER"),
        (Text, "TEXT"),
        (DateTime, "TIMESTAMP"),
        (Date, "DATE"),
    )
    model_sql    = _normalized_type(_column_type_sql(active_engine, model_column))
    database_sql = _normalized_type(database_type.compile(dialect=active_engine.dialect))

    for model_cls, database_prefix in simple_type_pairs:
        if isinstance(model_type, model_cls):
            return not database_sql.startswith(database_prefix) and model_sql != database_sql

    return model_sql != database_sql


def sync_existing_tables(active_engine) -> None:
    inspector       = inspect(active_engine)
    existing_tables = set(inspector.get_table_names())

    with active_engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue

            existing_columns = {
                column["name"]: column
                for column in inspector.get_columns(table.name)
            }

            for column in table.columns:
                table_name  = _quote(active_engine, table.name)
                column_name = _quote(active_engine, column.name)

                if column.name not in existing_columns:
                    column_definition = _safe_column_definition(active_engine, column)
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"))
                    print(f"Added column {table.name}.{column.name}")
                    continue

                if _should_alter_type(active_engine, column, existing_columns[column.name]):
                    type_sql = _column_type_sql(active_engine, column)
                    conn.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"ALTER COLUMN {column_name} TYPE {type_sql} "
                            f"USING {column_name}::{type_sql}"
                        )
                    )
                    print(f"Updated type {table.name}.{column.name} -> {type_sql}")


def create_tables(active_engine) -> None:
    import_registered_module_models()
    Base.metadata.create_all(bind=active_engine)
    sync_existing_tables(active_engine)


def seed_default_user(session_factory) -> None:
    db = session_factory()
    try:
        role = db.query(TBL_ROLE).filter(TBL_ROLE.id == DEFAULT_ROLE_ID).first()
        if not role:
            role = TBL_ROLE(
                id           = DEFAULT_ROLE_ID,
                name         = "SUPERUSER",
                name_lc      = "SUPERUSER",
                description  = "Default superuser role",
                is_superuser = True,
                is_active    = True,
            )
            db.add(role)

        user = db.query(TBL_USER).filter(TBL_USER.id == DEFAULT_USER_ID).first()
        if not user:
            user = TBL_USER(
                id         = DEFAULT_USER_ID,
                username   = DEFAULT_USERNAME,
                email      = "superuser@example.com",
                first_name = "SUPERUSER",
                last_name  = "SUPERUSER",
                phone      = "088888888",
                password   = pwd_context.hash(DEFAULT_PASSWORD),
                role_id    = DEFAULT_ROLE_ID,
                is_active  = True,
            )
            db.add(user)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_default_modules(session_factory) -> None:
    db = session_factory()
    try:
        category_module = db.query(TBL_MODULE).filter(TBL_MODULE.id == "MOD_CATEGORY").first()
        if not category_module:
            category_module = TBL_MODULE(
                id       = "MOD_CATEGORY",
                name     = "Category",
                name_lc  = "Category",
                url      = "/category",
                icon     = "i-lucide-tags",
                model    = "category",
                ordering = 1,
                active   = True,
            )
            db.add(category_module)

        category_sub_module = (
            db.query(TBL_SUB_MODULE)
            .filter(TBL_SUB_MODULE.id == "SMD_CATEGORY_LIST")
            .first()
        )
        if not category_sub_module:
            category_sub_module = TBL_SUB_MODULE(
                id        = "SMD_CATEGORY_LIST",
                module_id = "MOD_CATEGORY",
                name      = "Category List",
                name_lc   = "Category List",
                url       = "/category",
                icon      = "i-lucide-list",
                model     = "category",
                ordering  = 1,
                active    = True,
            )
            db.add(category_sub_module)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _sync_targets() -> list[tuple[str, str]]:
    targets = settings.CREATE_TABLE_TARGETS
    if "all" in targets:
        targets = ["local", "neon"]

    configured_targets = []
    for target in targets:
        if target == "local":
            configured_targets.append(("local", settings.LOCAL_DATABASE_URL))
            continue

        if target == "neon":
            if not settings.NEON_DATABASE_URL:
                raise RuntimeError("NEON_DATABASE_URL is empty. Add your Neon connection string to .env first.")
            configured_targets.append(("neon", settings.NEON_DATABASE_URL))
            continue

        raise RuntimeError(f"Unknown CREATE_TABLE_TARGETS value: {target}")

    seen_urls = set()
    unique_targets = []
    for name, database_url in configured_targets:
        if database_url in seen_urls:
            continue
        seen_urls.add(database_url)
        unique_targets.append((name, database_url))

    return unique_targets


def _create_engine(database_url: str):
    return create_engine(
        database_url,
        pool_timeout  = 30,
        pool_pre_ping = True,
    )


def sync_database(target_name: str, database_url: str) -> None:
    print(f"Syncing {target_name} database...")
    active_engine   = _create_engine(database_url)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=active_engine)

    try:
        create_tables(active_engine)
        seed_default_user(session_factory)
        seed_default_modules(session_factory)
    finally:
        active_engine.dispose()

    print(f"Done syncing {target_name} database.")


def run() -> None:
    for target_name, database_url in _sync_targets():
        sync_database(target_name, database_url)

    print("Done! Tables created and default user is ready in all configured databases.")
    print(f"Login username: {DEFAULT_USERNAME}")


if __name__ == "__main__":
    run()
