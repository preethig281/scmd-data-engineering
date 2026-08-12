import pandas as pd

CSV_PATH = "data/raw/scmd_provisional_202605.csv"

# Read codes as text so long SNOMED/ODS values aren't corrupted into numbers
df = pd.read_csv(CSV_PATH, dtype={
    "ODS_CODE": str,
    "VMP_SNOMED_CODE": str,
    "UNIT_OF_MEASURE_IDENTIFIER": str,
})

print("Rows:", len(df))
print("Columns:", list(df.columns))

print("\n--- Null counts per column ---")
print(df.isnull().sum())

print("\n--- Numeric ranges ---")
for col in ["TOTAL_QUANITY_IN_VMP_UNIT", "INDICATIVE_COST"]:
    print(col, "-> min:", df[col].min(), "max:", df[col].max())

print("\n--- Duplicate check ---")
key = ["YEAR_MONTH", "ODS_CODE", "VMP_SNOMED_CODE"]
dupes = df.duplicated(subset=key).sum()
print("Duplicate rows on", key, ":", dupes)

print("\n--- Negative value counts ---")
neg_qty = (df["TOTAL_QUANITY_IN_VMP_UNIT"] < 0).sum()
neg_cost = (df["INDICATIVE_COST"] < 0).sum()
print("Negative quantities:", neg_qty)
print("Negative costs:", neg_cost)