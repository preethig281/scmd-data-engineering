# Data Lineage — SCMD Pipeline

## Source
- **Origin:** NHS Trust pharmacy stock control systems (England)
- **Curated by:** Rx-Info, on behalf of NHS England
- **Published by:** NHSBSA Open Data Portal (CKAN)
- **Dataset:** Provisional Secondary Care Medicines Data (SCMD) with indicative price
- **Update frequency:** monthly, ~2 months in arrears
- **Format:** CSV, dm+d standard

## Flow Through the Pipeline
1. **Extract** — `src/extract.py` calls the CKAN API (`resource_show`) to get the current download URL, then downloads the monthly CSV to `data/raw/`. Download is size-verified against the API's reported byte count.
2. **Validate** — `src/validate.py` loads the raw CSV (codes forced to text), then checks row count, nulls, value ranges, negatives, and duplicates. Findings recorded in Week1_DataQuality_Report.md.
3. **Transform** — (Week 2+) clean types, handle negatives/reversals, standardise units.
4. **Load** — (Week 2+) write processed data to `data/processed/`.

## Provenance Notes
- Provisional data is later revised and republished as "Finalised" — the same month's figures can change over time.
- NHSBSA issued a correction notice (Jan 2026) for finalised files Apr 2019–Mar 2024, showing revisions do happen.
- Raw data is not committed to git (gitignored); it is always re-fetchable via extract.py.