import sqlite3
import pandas as pd
from pathlib import Path


def get_connection(db_path="data/warehouse/scmd.db"):
    """Open (and create, if needed) the SQLite warehouse."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn):
    """Create tables if they do not already exist (idempotent DDL)."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS dim_trust (
            ods_code TEXT PRIMARY KEY,
            organisation_name TEXT,
            trust_region TEXT
        );
        CREATE TABLE IF NOT EXISTS dim_medicine (
            vmp_snomed_code TEXT PRIMARY KEY,
            vmp_product_name TEXT,
            unit_of_measure_name TEXT
        );
        CREATE TABLE IF NOT EXISTS dim_date (
            year_month TEXT PRIMARY KEY,
            year INTEGER,
            month INTEGER
        );
        CREATE TABLE IF NOT EXISTS fact_medicines_issued (
            year_month TEXT NOT NULL REFERENCES dim_date(year_month),
            ods_code TEXT NOT NULL REFERENCES dim_trust(ods_code),
            vmp_snomed_code TEXT NOT NULL REFERENCES dim_medicine(vmp_snomed_code),
            total_quantity REAL,
            indicative_cost REAL,
            cost_per_unit REAL,
            cost_category TEXT,
            PRIMARY KEY (year_month, ods_code, vmp_snomed_code)
        );
    """)
    conn.commit()


def load_dimensions(conn, df):
    """Upsert dimension rows. Safe to call on every run."""
    trusts = df[["ODS_CODE"]].drop_duplicates().rename(columns={"ODS_CODE": "ods_code"})
    medicines = df[["VMP_SNOMED_CODE", "VMP_PRODUCT_NAME", "UNIT_OF_MEASURE_NAME"]].drop_duplicates().rename(columns={
        "VMP_SNOMED_CODE": "vmp_snomed_code",
        "VMP_PRODUCT_NAME": "vmp_product_name",
        "UNIT_OF_MEASURE_NAME": "unit_of_measure_name",
    })
    dates = df[["YEAR_MONTH", "year", "month"]].drop_duplicates().rename(columns={"YEAR_MONTH": "year_month"})

    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO dim_trust (ods_code) VALUES (?) ON CONFLICT(ods_code) DO NOTHING",
        trusts[["ods_code"]].values.tolist(),
    )
    cur.executemany(
        "INSERT INTO dim_medicine (vmp_snomed_code, vmp_product_name, unit_of_measure_name) "
        "VALUES (?, ?, ?) ON CONFLICT(vmp_snomed_code) DO UPDATE SET "
        "vmp_product_name = excluded.vmp_product_name, "
        "unit_of_measure_name = excluded.unit_of_measure_name",
        medicines.values.tolist(),
    )
    cur.executemany(
        "INSERT INTO dim_date (year_month, year, month) VALUES (?, ?, ?) "
        "ON CONFLICT(year_month) DO NOTHING",
        dates.astype(object).values.tolist(),
    )
    conn.commit()


def load_fact(conn, df, year_month):
    """Idempotent fact load for one month: delete this month's rows, then insert fresh."""
    cur = conn.cursor()
    cur.execute("DELETE FROM fact_medicines_issued WHERE year_month = ?", (year_month,))
    rows = df[[
        "YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE",
        "TOTAL_QUANTITY_IN_VMP_UNIT", "INDICATIVE_COST",
        "cost_per_unit", "cost_category",
    ]].astype(object).where(pd.notnull(df[[
        "YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE",
        "TOTAL_QUANTITY_IN_VMP_UNIT", "INDICATIVE_COST",
        "cost_per_unit", "cost_category",
    ]]), None).values.tolist()
    cur.executemany(
        "INSERT INTO fact_medicines_issued "
        "(year_month, ods_code, vmp_snomed_code, total_quantity, indicative_cost, cost_per_unit, cost_category) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return len(rows)


def load_scmd_to_db(parquet_path, db_path="data/warehouse/scmd.db"):
    """Orchestrate the full load: schema, dimensions, then fact (in that order)."""
    df = pd.read_parquet(parquet_path)
    year_month = str(df["YEAR_MONTH"].iloc[0])
    conn = get_connection(db_path)
    try:
        create_schema(conn)
        load_dimensions(conn, df)
        n = load_fact(conn, df, year_month)
        print(f"Loaded {n:,} fact rows for {year_month}")
        return n
    finally:
        conn.close()


if __name__ == "__main__":
    load_scmd_to_db("data/processed/scmd_202605_processed.parquet")
