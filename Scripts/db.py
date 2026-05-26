import os
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_engine():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set.")
    return create_engine(DATABASE_URL)

def query_df(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()
        return pd.DataFrame(rows, columns=list(columns))