from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = 'postgresql+psycopg://postgres:admin@127.0.0.1:5432/wallet'

engine = create_engine(DATABASE_URL)

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally: db.close()
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()