# Week 2 Transformation Report - SCMD May 2026

**Input:** data/raw/scmd_provisional_202605.csv (312,457 rows)
**Output:** data/processed/scmd_202605_processed.parquet (310,344 rows)
**Code:** src/transform.py
**Date:** August 2026

## What Changed

### Rows removed
- Removed 2,113 rows with negative quantity or cost (0.7% of the data).
- These represent stock returns or reversals, not medicines issued.
- Negative quantities and negative costs overlapped heavily (the same reversal transactions), so removing negative-quantity rows also cleared almost all negative-cost rows.

### Duplicates
- Checked for duplicates on the key YEAR_MONTH + ODS_CODE + VMP_SNOMED_CODE.
- 0 duplicates found, confirming the Week 1 finding that the grain is one row per trust, medicine, and month.

### Nulls
- 12,306 rows have a null INDICATIVE_COST (about 3.9%). These were KEPT with the cost left as NaN.
- Decision: a missing price is not the same as a price of zero. Filling with 0 would understate spend totals, so nulls are preserved for downstream users to handle knowingly.

### Types
- Code columns (ODS_CODE, VMP_SNOMED_CODE, UNIT_OF_MEASURE_IDENTIFIER) are read and kept as text to avoid numeric corruption of long identifiers.
- Quantity and cost are numeric (float).

## Columns Added (Enrichment)

1. cost_per_unit = INDICATIVE_COST / TOTAL_QUANITY_IN_VMP_UNIT
   - Where quantity is 0, the value is set to NaN to avoid divide-by-zero.

2. cost_category = low / medium / high
   - Based on cost quartiles: bottom 25% low, middle 50% medium, top 25% high.
   - Result: 74,528 low, 149,057 medium, 74,526 high, 12,233 with no category (null cost).

## Output Format
- Saved as Parquet (columnar, compressed) rather than CSV.
- Parquet is smaller, faster to query, and preserves data types (so codes stay text on reload).

## Verification
- 14 unit tests in tests/test_transform.py, all passing.
- 95% test coverage on src/transform.py.
- Tests cover normal cases and edge cases (null cost, zero quantity, divide-by-zero, real vs false duplicates).

## Summary
Raw data of 312,457 rows was cleaned to 310,344 trustworthy rows, enriched with 2 derived columns, and saved as an analysis-ready Parquet file. All transformation decisions are documented and tested.
