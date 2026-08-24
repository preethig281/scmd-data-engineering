# Architecture

## Overview
This is an ELT pipeline for NHS Secondary Care Medicines Data (SCMD). It extracts the monthly CSV
from the NHSBSA Open Data Portal, transforms it into clean enriched data, and loads it into a
SQLite warehouse for analysis.

## Data Flow
1. Extract: download the monthly SCMD CSV from the NHSBSA CKAN API (src/extract.py) to data/raw/.
2. Transform: clean nulls, remove negative reversals, dedup, add derived columns, standardize
   names, save as Parquet (src/transform.py) to data/processed/.
3. Quality gate: halt if the processed row count looks suspiciously low (src/validate.py).
4. Load: load the Parquet into a SQLite star schema, idempotently (src/load.py) to data/warehouse/.
5. Quality gate: halt if any fact row references a missing dimension (src/validate.py).

src/pipeline.py runs all stages with a single command.

## The Database (Week 3)
The warehouse now exists as a SQLite database at data/warehouse/scmd.db, organised as a star
schema: a central fact table (fact_medicines_issued, grain one Trust x Medicine x Month) surrounded
by dimension tables (dim_trust, dim_medicine, dim_date). It is reached with standard SQL and is the
input for Week 4 analysis. The database file is gitignored (large and re-creatable by rerunning the
pipeline). See docs/Week3_Schema_Design.md for the full schema and ERD.

## Key Design Decisions
1. Raw and processed data, and the database, are kept out of git (large, re-creatable).
2. SNOMED and ODS codes are handled as text to avoid numeric corruption.
3. The load is idempotent (delete-and-insert by month partition) so reruns are safe.

## Tech Stack
- Python (pandas, pyarrow, requests, sqlite3)
- SQLite for the warehouse
- pytest for testing
- Git and GitHub for version control
