# Week 1 Data Quality Report — SCMD May 2026

**File:** scmd_provisional_202605.csv
**Rows checked:** 312,457
**Method:** src/validate.py (pandas), run against all rows
**Date:** 12 Aug 2026

## Completeness
All eight columns are fully populated except INDICATIVE_COST, which has 12,306 nulls (~3.9%). These occur where no price mapping exists for a VMP. All identifier and quantity columns are 100% complete.

## Value Ranges
- TOTAL_QUANITY_IN_VMP_UNIT: −66,794,700 to 7,020,000
- INDICATIVE_COST: −£1,629,167.60 to £57,200,000

## Key Findings
1. **Negative values exist in both numeric columns.** 2,113 rows have a negative quantity and 2,040 have a negative cost (~0.7% of rows). These most likely represent returns, stock adjustments, or corrections rather than errors — expected in pharmacy stock-control data. Impact: naively summing quantity or cost will be reduced by these reversals, so they must be handled explicitly during aggregation.

2. **INDICATIVE_COST is incomplete.** 12,306 rows (~3.9%) have no cost. These should be treated as "unknown," not zero — treating them as zero would understate spend. Cost-based analysis must account for this gap.

3. **No true duplicates.** Zero rows repeat on the key YEAR_MONTH + ODS_CODE + VMP_SNOMED_CODE. This confirms the dataset's grain: one row per trust × medicine × month. The same medicine appearing under multiple trusts is expected and is not a duplicate.

4. **Codes must be treated as text.** VMP_SNOMED_CODE, ODS_CODE and UNIT_OF_MEASURE_IDENTIFIER are identifiers, not numbers. Reading them as numeric (e.g. opening in Excel) corrupts the long SNOMED codes into scientific notation. The validation script forces these to string on load.

5. **Wide value spread.** Both quantity and cost span a very large range, reflecting genuinely different medicines and pack sizes (e.g. a single high-cost specialist drug vs. bulk saline). Outliers are expected, not errors.

## Recommendations
- Handle negative quantities/costs explicitly in the transform step (flag or separate reversals before summing).
- Treat null INDICATIVE_COST as unknown, never zero.
- Load ODS_CODE, VMP_SNOMED_CODE and UNIT_OF_MEASURE_IDENTIFIER as strings in every script.
- Aggregate quantities only within a single unit of measure, since units differ across medicines.
- Carry the YEAR_MONTH + ODS_CODE + VMP_SNOMED_CODE key forward as the natural primary key.