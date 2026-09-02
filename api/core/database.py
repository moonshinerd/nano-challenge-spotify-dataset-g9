"""Configuração de conexão com o banco (engine, sessão, Base declarativa)."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/spotify")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessão por request e garante o close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
