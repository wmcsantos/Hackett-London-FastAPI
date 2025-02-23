from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from models import Base
from dotenv import load_dotenv
import os

# Load environemnt variables into the app
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_INFO")

if not DATABASE_URL:
    raise ValueError("DATABASE_INFO is not set in the .env file!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()