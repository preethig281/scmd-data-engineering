# SCMD Data Passport

| Field | Value |
|---|---|
| **Dataset** | Provisional SCMD with indicative price |
| **Source** | NHSBSA Open Data Portal (data from Rx-Info / NHS Trusts) |
| **Grain** | One row per trust × medicine (VMP) × month |
| **Primary key** | YEAR_MONTH + ODS_CODE + VMP_SNOMED_CODE |
| **Volume** | 312,457 rows (May 2026); ~35 MB/month |
| **Update cadence** | Monthly, ~2 months in arrears |
| **Licence** | Open Government Licence |

## Must-Know Caveats
- **Codes are text, not numbers** — SNOMED/ODS corrupt if read as numeric.
- **Header typo** — the quantity column is `TOTAL_QUANITY_IN_VMP_UNIT` (misspelled), in the source.
- **No trust names** — only ODS codes; needs a lookup to resolve.
- **Negatives exist** — 2,113 quantities, 2,040 costs (returns/adjustments); don't naively SUM.
- **~3.9% of costs are null** — treat as unknown, not zero.
- **Mixed units** — quantities aren't additive across different units of measure.
- **Provisional = revisable** — figures may change when finalised.

## Data Quality Summary (May 2026)
- Completeness: 100% except INDICATIVE_COST (12,306 nulls).
- Duplicates: none on the primary key.
- Validated by: src/validate.py.