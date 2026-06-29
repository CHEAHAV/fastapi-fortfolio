from core.runtime import require_project_venv

require_project_venv()

from typing import Any, Mapping
from passlib.context import CryptContext
from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, Text, inspect, text
from sqlalchemy.schema import CreateColumn
from core.api.role.models import TBL_ROLE
from core.api.user.models import TBL_USER
from core.api.module.models import TBL_MODULE
from core.api.sub_module.models import TBL_SUB_MODULE
from core.db import Base, SessionLocal, engine
from core.module_loader import import_registered_module_models


DEFAULT_ROLE_ID = "SUPERUSER"
DEFAULT_USER_ID = "SUPERUSER"
DEFAULT_USERNAME = "SuperUser"
DEFAULT_PASSWORD = "1qaz!QAZ"
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _quote(name: str) -> str:
    return engine.dialect.identifier_preparer.quote(name)


def _column_type_sql(column) -> str:
    return column.type.compile(dialect=engine.dialect)


def _safe_column_definition(column) -> str:
    definition = str(CreateColumn(column).compile(dialect=engine.dialect))
    if not column.primary_key:
        definition = definition.replace(" NOT NULL", "")
    return definition


def _normalized_type(value: str) -> str:
    return " ".join(value.upper().replace("CHARACTER VARYING", "VARCHAR").split())


def _should_alter_type(model_column, database_column: Mapping[str, Any]) -> bool:
    model_type = model_column.type
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
    model_sql = _normalized_type(_column_type_sql(model_column))
    database_sql = _normalized_type(database_type.compile(dialect=engine.dialect))

    for model_cls, database_prefix in simple_type_pairs:
        if isinstance(model_type, model_cls):
            return not database_sql.startswith(database_prefix) and model_sql != database_sql

    return model_sql != database_sql


def sync_existing_tables() -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue

            existing_columns = {
                column["name"]: column
                for column in inspector.get_columns(table.name)
            }

            for column in table.columns:
                table_name = _quote(table.name)
                column_name = _quote(column.name)

                if column.name not in existing_columns:
                    column_definition = _safe_column_definition(column)
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"))
                    print(f"Added column {table.name}.{column.name}")
                    continue

                if _should_alter_type(column, existing_columns[column.name]):
                    type_sql = _column_type_sql(column)
                    conn.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"ALTER COLUMN {column_name} TYPE {type_sql} "
                            f"USING {column_name}::{type_sql}"
                        )
                    )
                    print(f"Updated type {table.name}.{column.name} -> {type_sql}")


def create_tables() -> None:
    import_registered_module_models()
    Base.metadata.create_all(bind=engine)
    sync_existing_tables()


def seed_default_user() -> None:
    db = SessionLocal()
    try:
        role = db.query(TBL_ROLE).filter(TBL_ROLE.id == DEFAULT_ROLE_ID).first()
        if not role:
            role = TBL_ROLE(
                id=DEFAULT_ROLE_ID,
                name="SUPERUSER",
                name_lc="SUPERUSER",
                description="Default superuser role",
                is_superuser=True,
                is_active=True,
            )
            db.add(role)

        user = db.query(TBL_USER).filter(TBL_USER.id == DEFAULT_USER_ID).first()
        if not user:
            user = TBL_USER(
                id=DEFAULT_USER_ID,
                username=DEFAULT_USERNAME,
                email="superuser@example.com",
                first_name="SUPERUSER",
                last_name="SUPERUSER",
                phone="088888888",
                password=pwd_context.hash(DEFAULT_PASSWORD),
                role_id=DEFAULT_ROLE_ID,
                is_active=True,
            )
            db.add(user)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_default_modules() -> None:
    db = SessionLocal()
    try:
        category_module = db.query(TBL_MODULE).filter(TBL_MODULE.id == "MOD_CATEGORY").first()
        if not category_module:
            category_module = TBL_MODULE(
                id="MOD_CATEGORY",
                name="Category",
                name_lc="Category",
                url="/category",
                icon="i-lucide-tags",
                model="category",
                ordering=1,
                active=True,
            )
            db.add(category_module)

        category_sub_module = (
            db.query(TBL_SUB_MODULE)
            .filter(TBL_SUB_MODULE.id == "SMD_CATEGORY_LIST")
            .first()
        )
        if not category_sub_module:
            category_sub_module = TBL_SUB_MODULE(
                id="SMD_CATEGORY_LIST",
                module_id="MOD_CATEGORY",
                name="Category List",
                name_lc="Category List",
                url="/category",
                icon="i-lucide-list",
                model="category",
                ordering=1,
                active=True,
            )
            db.add(category_sub_module)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def run() -> None:
    create_tables()
    seed_default_user()
    seed_default_modules()
    print("Done! Tables created and default user is ready.")
    print(f"Login username: {DEFAULT_USERNAME}")


if __name__ == "__main__":
    run()
