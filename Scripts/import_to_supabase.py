"""
Run this ONCE locally to import all CSV files into Supabase.
Usage: python Scripts/import_to_supabase.py
Set DATABASE_URL environment variable first.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Set DATABASE_URL environment variable first.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Data", "Processed")
engine = create_engine(DATABASE_URL)

files = {
    "traffic":       "traffic_clean.csv",
    "ads":           "ads_clean.csv",
    "logs":          "logs_clean.csv",
    "retail":        "retail_clean.csv",
    "user_behavior": "user_behavior_clean.csv",
}

for table, filename in files.items():
    path = os.path.join(DATA_DIR, filename)
    print(f"Importing {filename} → table '{table}'...")
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    df.to_sql(table, engine, if_exists="replace", index=False, chunksize=1000)
    print(f"{len(df):,} rows imported into '{table}'")

print("\nAll tables imported successfully!")