if __name__ == "__main__":
    df = load_raw("data/raw/scmd_provisional_202605.csv")
    df = remove_negatives(df)
    df = deduplicate(df)
    df = add_derived_columns(df)
    print(f"\nFinal rows: {len(df):,}, columns: {len(df.columns)}")
    print(df[["INDICATIVE_COST", "cost_per_unit", "cost_category"]].head())