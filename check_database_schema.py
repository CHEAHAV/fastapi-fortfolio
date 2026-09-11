"""Compare local PostgreSQL with Neon; optionally add missing schema objects.

Never copies rows, drops objects, or changes existing column definitions.
"""
import argparse
import json

from sqlalchemy import MetaData, create_engine, inspect, text
from sqlalchemy.schema import CreateColumn

from config import settings
from core.runtime import require_project_venv


def schema_snapshot(connection):
    inspector = inspect(connection)
    return {
        table: {
            column["name"]: {
                "type": str(column["type"].compile(dialect=connection.dialect)),
                "nullable": column["nullable"],
                "default": column["default"],
            }
            for column in inspector.get_columns(table)
        }
        for table in inspector.get_table_names()
    }


def compare_schemas(source, target):
    return {
        "missing_tables": sorted(set(source) - set(target)),
        "missing_columns": {
            table: sorted(set(columns) - set(target[table]))
            for table, columns in source.items()
            if table in target and set(columns) - set(target[table])
        },
        "different_columns": {
            f"{table}.{column}": {"local": definition, "neon": target[table][column]}
            for table, columns in source.items()
            for column, definition in columns.items()
            if column in target.get(table, {}) and definition != target[table][column]
        },
    }


def add_missing_schema(source_connection, target_connection):
    metadata = MetaData()
    metadata.reflect(bind=source_connection)
    source = schema_snapshot(source_connection)
    target = schema_snapshot(target_connection)
    differences = compare_schemas(source, target)
    additions = [
        metadata.tables[table].c[column]
        for table, columns in differences["missing_columns"].items()
        for column in columns
    ]
    # Existing rows need an explicit backfill for required/generated fields.
    # Reject the whole plan before executing DDL rather than inventing values.
    if any(not c.nullable or c.primary_key or c.foreign_keys or
           c.server_default is not None or c.computed is not None or
           c.identity is not None for c in additions):
        raise RuntimeError("Missing required/generated columns need a dedicated migration")
    metadata.create_all(
        bind=target_connection,
        tables=[metadata.tables[name] for name in differences["missing_tables"]],
    )
    quote = target_connection.dialect.identifier_preparer.quote
    for column in additions:
        definition = str(CreateColumn(column).compile(dialect=target_connection.dialect))
        target_connection.execute(text(
            f"ALTER TABLE {quote(column.table.name)} ADD COLUMN {definition}"
        ))


def run():
    require_project_venv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-missing", action="store_true")
    args = parser.parse_args()
    if not settings.NEON_DATABASE_URL:
        raise RuntimeError("NEON_DATABASE_URL is not configured")
    local = create_engine(settings.LOCAL_DATABASE_URL, connect_args={"connect_timeout": 10})
    neon = create_engine(settings.NEON_DATABASE_URL, connect_args={"connect_timeout": 10})
    try:
        with local.connect() as source, neon.begin() as target:
            if args.apply_missing:
                target.execute(text("SET LOCAL lock_timeout = '5s'"))
                target.execute(text("SET LOCAL statement_timeout = '30s'"))
                add_missing_schema(source, target)
            source_schema = schema_snapshot(source)
            target_schema = schema_snapshot(target)
            differences = compare_schemas(source_schema, target_schema)
            print(json.dumps({
                "local": {"tables": len(source_schema), "columns": sum(map(len, source_schema.values()))},
                "neon": {"tables": len(target_schema), "columns": sum(map(len, target_schema.values()))},
                **differences,
            }, indent=2))
        return 1 if any(differences.values()) else 0
    finally:
        local.dispose()
        neon.dispose()


if __name__ == "__main__":
    raise SystemExit(run())
