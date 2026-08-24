import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from transform import transform_pipeline
from load import load_scmd_to_db, get_connection
from validate import check_row_count_drift, check_referential_integrity

RAW_PATH = "data/raw/scmd_provisional_202605.csv"
PROCESSED_PATH = "data/processed/scmd_202605_processed.parquet"
DB_PATH = "data/warehouse/scmd.db"


def run_pipeline():
    """Run the full SCMD pipeline: Transform, gate-check, Load, gate-check."""
    print("=" * 50)
    print("SCMD PIPELINE - START")
    print("=" * 50)

    print("\nStep 1: Transform (clean + enrich)")
    transform_pipeline(RAW_PATH, PROCESSED_PATH)

    print("\nStep 2: Quality gate - input row count")
    if not check_row_count_drift(PROCESSED_PATH):
        raise ValueError("Row count gate failed; aborting before load")

    print("\nStep 3: Load (into warehouse)")
    n_loaded = load_scmd_to_db(PROCESSED_PATH, DB_PATH)
    print(f"Loaded {n_loaded:,} rows into {DB_PATH}")

    print("\nStep 4: Quality gate - referential integrity")
    conn = get_connection(DB_PATH)
    try:
        if not check_referential_integrity(conn):
            raise ValueError("Referential integrity gate failed after load")
    finally:
        conn.close()

    print("\n" + "=" * 50)
    print("SCMD PIPELINE - COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()
