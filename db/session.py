from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

# Define the SQLAlchemy engine and sessionmaker
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)  # Add echo=True for SQL logging, if needed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DBSession:
    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
