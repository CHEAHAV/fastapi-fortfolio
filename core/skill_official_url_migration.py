"""Add the skill link column and backfill existing technologies once."""
import re

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from core.technology_urls import OFFICIAL_URLS


def migrate_skill_official_url(engine: Engine) -> tuple[bool, int]:
    """Touch only tbl_skill; retain all existing rows and customized links.

    Backfill only when adding the column, so rerunning the migration also
    preserves links intentionally cleared through the API after migration.
    """
    with engine.begin() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("tbl_skill"):
            raise RuntimeError("tbl_skill does not exist; run create_table.py first")
        if "official_url" in {column["name"] for column in inspector.get_columns("tbl_skill")}:
            return False, 0

        connection.execute(text("ALTER TABLE tbl_skill ADD COLUMN official_url VARCHAR(2048)"))
        rows = connection.execute(text("SELECT id, name FROM tbl_skill")).mappings()
        updated = 0
        for row in rows:
            key = re.sub(r"[\s._-]+", "", (row["name"] or "").lower())
            url = OFFICIAL_URLS.get(key)
            if url:
                connection.execute(text(
                    "UPDATE tbl_skill SET official_url = :url WHERE id = :id"
                ), {"url": url, "id": row["id"]})
                updated += 1
        return True, updated
