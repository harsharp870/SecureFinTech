import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

db_url = settings.active_database_url
if os.getenv("USE_SQLITE", "true").lower() in ("true", "1") or not settings.DATABASE_URL:
    db_url = "sqlite:///./securefintech.db"

engine_kwargs = {}
if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(db_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
