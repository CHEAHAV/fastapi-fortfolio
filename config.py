import os
import re
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse

root_path = str(Path('.'))
env_path  = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
image_path = '%s/images/'%os.getenv('S3_URL') if os.getenv('FILE_STORAGE') == 'S3' else "%s/static/images/"%(os.getenv("APP_URL"))

def _env_list(*names, default=''):
    values = []
    for name in names:
        raw_value = os.getenv(name, '')
        values.extend(value.strip() for value in raw_value.split(','))
    values = [value for value in values if value]
    if values:
        return list(dict.fromkeys(values))
    return [default] if default else []

def _normalize_database_url(database_url: str) -> str:
    database_url = re.sub(r"\s*([=&?])\s*", r"\1", database_url.strip())
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url

def _build_local_database_url() -> str:
    local_database_url = os.getenv("LOCAL_DATABASE_URL", "").strip()
    if local_database_url:
        return _normalize_database_url(local_database_url)

    user     = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    server   = os.getenv("DB_SERVER", "localhost")
    port     = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "tdd")
    return f"postgresql://{user}:{password}@{server}:{port}/{database}"

def _build_neon_database_url() -> str:
    return _normalize_database_url(os.getenv("NEON_DATABASE_URL", "").strip())

def _build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        return _normalize_database_url(database_url)

    db_target = os.getenv("DB_TARGET", "local").strip().lower()
    if db_target == "neon":
        neon_database_url = _build_neon_database_url()
        if neon_database_url:
            return neon_database_url

    return _build_local_database_url()

def _database_name_from_url(database_url: str, default: str) -> str:
    path = urlparse(database_url).path.strip("/")
    return path or default

# Central Configuration
SYNC_CENTRAL     = os.getenv("SYNC_CENTRAL", "false").lower() == "true"
CENTRAL_API_KEY  = os.getenv("CENTRAL_API_KEY", "")
CENTRAL_BASE_URL = os.getenv("CENTRAL_BASE_URL", "")

class Settings:
    PROJECT_NAME        :str  = "Online Shop Backend API"
    POS_PROJECT_NAME    :str  = "Online Shop POS API"
    MOBILE_PROJECT_NAME :str  = "Online Shop Mobile API"
    PROJECT_VERSION     :str  = "1.0.0"
    
    APP_URL      = os.getenv("APP_URL", "").strip()
    FRONTEND_URL = os.getenv("FRONTEND_URL", "").strip()
    ORIGINS      = _env_list("CORS_ORIGINS", "ALLOWED_HOSTS", "FRONTEND_URL", default="*")
    
    SECRET_KEY                  = os.getenv("SECRET_KEY", "469efa472104afa04213fec4aca08038f37babd0f1b9f5126daa58dd4263f745")
    ALGORITHM                   = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))

    FIREBASE_CREDENTIAL_PATH = os.getenv("FIREBASE_CREDENTIAL_PATH", "")

    POSTGRES_USER     : str = os.getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD: str  = os.getenv("DB_PASSWORD", "")
    POSTGRES_SERVER   : str = os.getenv("DB_SERVER","localhost")
    POSTGRES_PORT     : str = os.getenv("DB_PORT", "5432")
    LOCAL_DATABASE_URL = _build_local_database_url()
    NEON_DATABASE_URL  = _build_neon_database_url()
    CREATE_TABLE_TARGETS = [
        target.strip().lower()
        for target in os.getenv("CREATE_TABLE_TARGETS", "local,neon").split(",")
        if target.strip()
    ]
    MIRROR_DATABASE_WRITES = os.getenv("MIRROR_DATABASE_WRITES", "false").strip().lower() == "true"
    DATABASE_URL = _build_database_url()
    POSTGRES_DB : str = _database_name_from_url(DATABASE_URL, os.getenv("DB_NAME","tdd"))

    MAX_DAY_PER_MONTH = 1.5
    MISSED_AFTER      = 2
    
    # AES Encryption
    AES_SECRET_KEY = os.getenv("AES_SECRET_KEY", "469efa472104afa04213fec4aca08038f37babd0f1b9f5126daa58dd4263f745")

    # Central Configuration
    CELERY_BROKER_URL     = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    
    CYTHON_OUTPUT_DIR = os.getenv("CYTHON_OUTPUT_DIR", "generated")
    VERSION = os.getenv("VERSION", "1.0.0")

settings = Settings()
