import os
from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set.")
    return create_engine(DATABASE_URL)

def query_df(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)