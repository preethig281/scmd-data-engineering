# Week 2 Transformation Strategy — SCMD

## Guiding principles
1. Keep data unless it is genuinely unusable.
2. Document every decision and its trade-off.
3. Never silently drop rows: always count and log what changes.

## Key decisions

### Null INDICATIVE_COST (12,306 rows, ~3.9%)
Decision: keep the row, leave the cost as NaN (do not fill with 0).
Reason: a missing price is not the same as a £0 price. Filling with 0 would understate spend totals downstream. The row still has a valid medicine and quantity, so it is useful.
Trade-off: the clean file still contains nulls in this column, which downstream steps must handle. Parquet stores NaN without issue.

### Negative quantities and costs (2,113 negative quantities, 2,040 negative costs)
Decision: remove these rows from the clean dataset; record the counts and reason in the transformation report.
Reason: negatives represent stock returns/reversals, not medicines issued. The Week 2 output must pass a "no negative quantities or costs" quality gate, so they are removed from the processed file but documented so the information is not lost.
Trade-off: loses ~0.7% of rows; those events are no longer in the clean file (could be saved separately later if needed).

## Column-by-column plan

### YEAR_MONTH
- Input: integer, format YYYYMM (e.g. 202605); no nulls
- Output: keep as integer YYYYMM (already consistent and analysis-friendly)
- Cleaning: none needed
- Validation: all values equal 202605 for this file; no nulls

### ODS_CODE
- Input: text (string), e.g. RA2; no nulls
- Output: text, unchanged
- Cleaning: keep as string (identifier, never a number); strip any stray whitespace
- Validation: no nulls; all values non-empty

### VMP_SNOMED_CODE
- Input: text (string), long numeric-looking identifier; no nulls
- Output: text, unchanged
- Cleaning: keep as string to avoid numeric corruption
- Validation: no nulls; every row has a code

### VMP_PRODUCT_NAME
- Input: text (string); no nulls
- Output: text, unchanged
- Cleaning: strip whitespace; drop any row where this is blank (can't identify the medicine)
- Validation: no nulls or blank names remain

### UNIT_OF_MEASURE_IDENTIFIER and UNIT_OF_MEASURE_NAME
- Input: identifier is a numeric-looking code (kept as text); name is text (TABLET, ML, etc.); no nulls
- Output: both text, unchanged
- Cleaning: keep identifier as string; keep the pair together
- Validation: no nulls; identifier and name are consistent (1:1)

### TOTAL_QUANITY_IN_VMP_UNIT
- Input: float (header misspelled "QUANITY"); 2,113 negatives; range −66.8M to 7.02M; no nulls
- Output: float; no negatives
- Cleaning: convert to numeric; drop negative-quantity rows (reversals)
- Validation: no negative quantities remain; column is numeric

### INDICATIVE_COST
- Input: float; 12,306 nulls; 2,040 negatives; range −£1.63M to £57.2M
- Output: float; no negatives; nulls kept as NaN
- Cleaning: convert to numeric; drop negative-cost rows; keep nulls as NaN
- Validation: no negative costs remain; null count logged

## Derived columns to add
1. cost_per_unit = INDICATIVE_COST / TOTAL_QUANITY_IN_VMP_UNIT
   - Rule: if quantity is 0 or cost is null, set cost_per_unit to NaN (avoid divide-by-zero and misleading values)
2. cost_category = high / medium / low
   - Based on quartiles of INDICATIVE_COST: bottom 25% = low, middle 50% = medium, top 25% = high (using pd.qcut)
3. trust_region = mapped from ODS_CODE via a lookup table
   - Note: deferred/partial for now — full ODS-to-region lookup is a later enrichment; will map where a lookup is available and leave the rest as "Unknown"

## Trade-offs & assumptions
- Removing negatives loses ~0.7% of rows but ensures totals are not distorted by reversals.
- Keeping null costs as NaN preserves honesty at the cost of downstream null-handling.
- Deduplication is a safety step: Week 1 confirmed 0 duplicates on YEAR_MONTH + ODS_CODE + VMP_SNOMED_CODE, but the transform still runs the check in case a future month differs.
- cost_category uses cost quartiles rather than cost_per_unit, since total indicative cost is the figure analysts most often bucket by.