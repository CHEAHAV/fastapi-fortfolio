from sqlalchemy import create_engine, select
from sqlalchemy.dialects.postgresql import insert

from config import settings
from core.db import Base
from core.module_loader import import_registered_module_models


def _engine(database_url: str):
    return create_engine(
        database_url,
        pool_timeout  = 30,
        pool_pre_ping = True,
    )


def copy_local_to_neon() -> None:
    if not settings.NEON_DATABASE_URL:
        raise RuntimeError("NEON_DATABASE_URL is empty. Add your Neon connection string to .env first.")

    import_registered_module_models()

    local_engine = _engine(settings.LOCAL_DATABASE_URL)
    neon_engine = _engine(settings.NEON_DATABASE_URL)

    try:
        with local_engine.connect() as source, neon_engine.begin() as target:
            for table in Base.metadata.sorted_tables:
                rows = source.execute(select(table)).mappings().all()
                if not rows:
                    continue

                primary_keys = [column.name for column in table.primary_key.columns]
                if not primary_keys:
                    continue

                statement = insert(table).values([dict(row) for row in rows])
                update_columns = {
                    column.name: statement.excluded[column.name]
                    for column in table.columns
                    if column.name not in primary_keys
                }
                statement = statement.on_conflict_do_update(
                    index_elements=primary_keys,
                    set_=update_columns,
                )
                target.execute(statement)
                print(f"Copied {len(rows)} rows to Neon: {table.name}")
    finally:
        local_engine.dispose()
        neon_engine.dispose()


def run() -> None:
    copy_local_to_neon()
    print("Done! Local data copied to Neon.")
