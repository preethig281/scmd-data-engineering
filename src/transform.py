import pandas as pd

# Columns that must stay text so long codes aren't corrupted
TEXT_COLUMNS = {
    "ODS_CODE": str,
    "VMP_SNOMED_CODE": str,
    "UNIT_OF_MEASURE_IDENTIFIER": str,
}


def load_raw(filepath):
    """Load the raw SCMD CSV, keeping code columns as text."""
    df = pd.read_csv(filepath, dtype=TEXT_COLUMNS)
    print(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    return df


def remove_negatives(df):
    """Remove rows with negative quantity or cost (stock reversals). Logs how many."""
    before = len(df)

    df = df[df["TOTAL_QUANITY_IN_VMP_UNIT"] >= 0]
    df = df[df["INDICATIVE_COST"].isna() | (df["INDICATIVE_COST"] >= 0)]

    removed = before - len(df)
    print(f"Removed {removed:,} negative rows ({removed / before:.1%})")
    return df


def deduplicate(df):
    """Drop any exact duplicate rows on the natural key. Logs how many."""
    key = ["YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE"]
    before = len(df)
    df = df.drop_duplicates(subset=key)
    removed = before - len(df)
    print(f"Removed {removed:,} duplicate rows")
    return df


def add_derived_columns(df):
    """Add cost_per_unit and cost_category derived columns."""
    # cost_per_unit: cost divided by quantity; NaN where quantity is 0 (avoid divide-by-zero)
    df["cost_per_unit"] = df["INDICATIVE_COST"] / df["TOTAL_QUANITY_IN_VMP_UNIT"].replace(0, pd.NA)

    # cost_category: low / medium / high based on cost quartiles
    df["cost_category"] = pd.qcut(
        df["INDICATIVE_COST"],
        q=[0, 0.25, 0.75, 1.0],
        labels=["low", "medium", "high"],
    )

    print("Added derived columns: cost_per_unit, cost_category")
    return df


def save_parquet(df, output_path):
    """Save the processed DataFrame to Parquet."""
    df.to_parquet(output_path, index=False)
    print(f"Saved {len(df):,} rows to {output_path}")


if __name__ == "__main__":
    df = load_raw("data/raw/scmd_provisional_202605.csv")
    df = remove_negatives(df)
    df = deduplicate(df)
    df = add_derived_columns(df)
    print(f"\nFinal rows: {len(df):,}, columns: {len(df.columns)}")
    print(df[["INDICATIVE_COST", "cost_per_unit", "cost_category"]].head())
    print(df["cost_category"].value_counts(dropna=False))
    save_parquet(df, "data/processed/scmd_202605_processed.parquet")