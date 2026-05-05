import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada no arquivo .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_connection():
    return engine.connect()


def execute_query(query: str, params: dict | None = None):
    with engine.begin() as conn:
        conn.execute(text(query), params or {})


def fetch_dataframe(query: str, params: dict | None = None):
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn, params=params or {})


if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()"))
            print("Conexão OK:", result.fetchone())
    except Exception as e:
        print("Erro na conexão:", e)