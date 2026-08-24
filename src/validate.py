import pandas as pd
from load import get_connection


def check_row_count_drift(parquet_path, expected_min=280000):
    """Halt if the source file looks suspiciously small (silent data loss upstream)."""
    n = len(pd.read_parquet(parquet_path))
    if n < expected_min:
        print(f"FAILED: row count gate - {n:,} rows (expected >= {expected_min:,})")
        return False
    print(f"PASSED: row count gate - {n:,} rows")
    return True


def check_referential_integrity(conn):
    """Halt if any fact row references a trust/medicine/date not in the dimensions."""
    orphans = conn.execute("""
        SELECT COUNT(*) FROM fact_medicines_issued f
        LEFT JOIN dim_trust t ON f.ods_code = t.ods_code
        LEFT JOIN dim_medicine m ON f.vmp_snomed_code = m.vmp_snomed_code
        LEFT JOIN dim_date d ON f.year_month = d.year_month
        WHERE t.ods_code IS NULL OR m.vmp_snomed_code IS NULL OR d.year_month IS NULL
    """).fetchone()[0]
    if orphans > 0:
        print(f"FAILED: referential integrity gate - {orphans:,} orphaned fact rows")
        return False
    print("PASSED: referential integrity gate")
    return True
