import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use DATABASE_URL if set (e.g., Postgres in prod), otherwise local SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trypsync.db")

engine = create_engine(
    DATABASE_URL,
    # For SQLite, allow usage from multiple threads (FastAPI dev server).
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes.
    Opens a new SQLAlchemy Session for the duration of the request
    and closes it afterwards.
    """
    from sqlalchemy.orm import Session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

