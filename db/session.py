from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.config import settings

Base = declarative_base()

if settings.sync_database_url.startswith("sqlite"):
    sync_engine = create_engine(
        settings.sync_database_url,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False}
    )
else:
    sync_engine = create_engine(
        settings.sync_database_url,
        echo=settings.DB_ECHO,
        pool_size=20,
        max_overflow=10,
        pool_recycle=3600,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
