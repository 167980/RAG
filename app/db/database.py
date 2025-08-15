from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("postgresql+psycopg2://postgres:postgres@postgres-db:5432/new_project")


#create SQLAlchemy engine and session
# engine = create_engine("postgresql://postgres:dibya@localhost:5432/new_project")
engine = create_engine("postgresql+psycopg2://postgres:postgres@postgres-db:5432/new_project")
#create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
#base class for models
Base = declarative_base()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()