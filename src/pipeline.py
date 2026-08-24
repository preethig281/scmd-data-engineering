import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from transform import transform_pipeline

RAW_PATH = "data/raw/scmd_provisional_202605.csv"
PROCESSED_PATH = "data/processed/scmd_202605_processed.parquet"


def run_pipeline():
    """Run the full SCMD pipeline: transform the raw CSV into a clean Parquet file."""
    print("=" * 50)
    print("SCMD PIPELINE - START")
    print("=" * 50)

    print("\nStep 1: Transform (clean + enrich)")
    transform_pipeline(RAW_PATH, PROCESSED_PATH)

    print("\n" + "=" * 50)
    print("SCMD PIPELINE - COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()
