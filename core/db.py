from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from config import settings

Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL,
    pool_timeout=30,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Backward-compatible alias for older code in this project.
Session = SessionLocal
db = SessionLocal()
