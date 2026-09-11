"""Run the focused my-core migration without syncing unrelated tables."""
import argparse

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from core.runtime import require_project_venv
from core.mycore_official_url_migration import migrate_mycore_official_url


def main() -> None:
    require_project_venv()
    from config import settings

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["local", "neon"], default="local")
    arguments = parser.parse_args()
    url = settings.LOCAL_DATABASE_URL if arguments.target == "local" else settings.NEON_DATABASE_URL
    if not url:
        raise SystemExit(f"The {arguments.target} database is not configured")
    engine = create_engine(url, connect_args={"connect_timeout": 10})
    try:
        added, count = migrate_mycore_official_url(engine)
        print(f"{arguments.target}: official_url {'added' if added else 'already exists'}; {count} competencies populated.")
    except SQLAlchemyError as error:
        # Connection exceptions may contain database credentials; don't print them.
        raise SystemExit(f"Migration failed ({type(error).__name__}); check database connectivity.") from None
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
