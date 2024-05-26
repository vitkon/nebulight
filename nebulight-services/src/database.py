from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import SUPABASE_URL, SUPABASE_KEY

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres.jkqzhukcmllqdedmvmzu:All4You2024#@aws-0-eu-west-2.pooler.supabase.com:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()