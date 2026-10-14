import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# We use SQLite by default. On Vercel serverless, root filesystem is read-only, so use /tmp.
default_db = "sqlite:////tmp/smartconsent.db" if os.getenv("VERCEL") else "sqlite:///./smartconsent.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", default_db)

# connect_args is needed only for SQLite
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
