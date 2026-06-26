from passlib.context import CryptContext

from core.api.role.models import TBL_ROLE
from core.api.user.models import TBL_USER
from core.db import Base, SessionLocal, engine
from core.module_loader import import_registered_module_models


DEFAULT_ROLE_ID = "SUPERUSER"
DEFAULT_USER_ID = "SUPERUSER"
DEFAULT_USERNAME = "SuperUser"
DEFAULT_PASSWORD = "1qaz!QAZ"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_tables() -> None:
    import_registered_module_models()
    Base.metadata.create_all(bind=engine)


def create_user_and_role() -> None:
    db = SessionLocal()
    try:
        role_obj = db.query(TBL_ROLE).filter(TBL_ROLE.id == DEFAULT_ROLE_ID).first()
        if not role_obj:
            print("create role=============")
            role_obj = TBL_ROLE(
                id=DEFAULT_ROLE_ID,
                name="SUPERUSER",
                name_lc="SUPERUSER",
                description="Superuser",
                is_superuser=True,
                is_active=True,
            )
            db.add(role_obj)

        user_obj = db.query(TBL_USER).filter(TBL_USER.id == DEFAULT_USER_ID).first()
        if not user_obj:
            print("create user=============")
            user_obj = TBL_USER(
                id=DEFAULT_USER_ID,
                first_name="SUPERUSER",
                last_name="SUPERUSER",
                email="superuser@example.com",
                username=DEFAULT_USERNAME,
                phone="088888888",
                password=get_password_hash(DEFAULT_PASSWORD),
                role_id=DEFAULT_ROLE_ID,
                photo="",
                is_active=True,
            )
            db.add(user_obj)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def run() -> None:
    create_tables()
    create_user_and_role()
    print("Done! Tables created and default user is ready.")


if __name__ == "__main__":
    run()
