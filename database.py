import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use DATABASE_URL if set (e.g., Postgres in prod), otherwise local SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trypsync.db")

# Configure connection args based on database type
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # For SQLite (local dev), allow usage from multiple threads (FastAPI dev server).
    connect_args = {"check_same_thread": False}
elif DATABASE_URL.startswith("postgresql") or "supabase" in DATABASE_URL.lower():
    # Supabase/PostgreSQL requires SSL encryption
    connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using (prevents stale connections)
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    # Import models so Base.metadata knows about them
    import models
    Base.metadata.create_all(bind=engine)

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

