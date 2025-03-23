from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .models import Base
from dotenv import load_dotenv
import os

# Load environemnt variables into the app
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_INFO is not set in the .env file!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This will create the tables if they don’t exist
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    db.execute(text("SET search_path TO hackettshop;"))
    try:
        yield db
    finally:
        db.close()