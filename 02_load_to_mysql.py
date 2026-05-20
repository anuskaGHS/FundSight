# =============================================================
# FundSight — Step 2: Load Cleaned Data into MySQL
# =============================================================
# Reads : data/cleaned_startup_funding.csv
# Creates MySQL database: fundsight
# Creates table: startup_funding
# Loads all 3196 rows into the table
# =============================================================

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

# ─────────────────────────────────────────
# 1. LOAD ENVIRONMENT VARIABLES
# ─────────────────────────────────────────

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# ─────────────────────────────────────────
# 2. CREATE DATABASE IF NOT EXISTS
# ─────────────────────────────────────────

# First connect without specifying a database
encoded_password = quote_plus(DB_PASSWORD)
engine_root = create_engine(
    f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}"
)

with engine_root.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    print(f"✅ Database '{DB_NAME}' ready")

# ─────────────────────────────────────────
# 3. CONNECT TO THE FUNDSIGHT DATABASE
# ─────────────────────────────────────────

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}/{DB_NAME}"
)

# ─────────────────────────────────────────
# 4. LOAD CLEANED CSV
# ─────────────────────────────────────────

df = pd.read_csv("data/cleaned_startup_funding.csv")
print(f"📂 Loaded {len(df)} rows from cleaned_startup_funding.csv")

# ─────────────────────────────────────────
# 5. LOAD INTO MYSQL TABLE
# ─────────────────────────────────────────

# if_exists="replace" drops and recreates the table each run
# This is safe during development — we can always reload from CSV

df.to_sql(
    name="startup_funding",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=500
)

print(f"✅ Loaded {len(df)} rows into MySQL table 'startup_funding'")

# ─────────────────────────────────────────
# 6. VERIFY — READ BACK FROM MySQL
# ─────────────────────────────────────────

with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM startup_funding"))
    count = result.fetchone()[0]
    print(f"✅ Verified: {count} rows in MySQL table")

    result2 = conn.execute(text("""
        SELECT sector, COUNT(*) as deals
        FROM startup_funding
        GROUP BY sector
        ORDER BY deals DESC
        LIMIT 5
    """))
    print("\nTop 5 sectors in MySQL:")
    for row in result2:
        print(f"  {row[0]:<25} {row[1]} deals")