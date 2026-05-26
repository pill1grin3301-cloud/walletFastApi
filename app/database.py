import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# database.py
DATABASE_URL = os.getenv("DATABASE_URL", 'postgresql+psycopg://postgres:admin@wallet_db:5432/wallet')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()