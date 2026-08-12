# Architecture

## Overview
This is an ELT pipeline for NHS Secondary Care Medicines Data. It extracts the monthly CSV from the NHSBSA Open Data Portal, loads it in raw form, and transforms it into clean, analysis ready tables.

## Data Flow
1. Extract: download the monthly SCMD CSV from the NHSBSA portal via the CKAN API (src/extract.py).
2. Validate: check row counts, nulls, value ranges, negatives, and duplicates (src/validate.py).
3. Transform: clean and standardise the data, for example fixing types and handling the negative quantity and cost values (src/transform.py).
4. Load: write the processed data to data/processed/ (src/load.py).

## Key Design Decisions
1. Raw data is kept out of git because it is large and re-downloadable (see .gitignore).
2. SNOMED and ODS codes are handled as text to avoid numeric corruption.
3. The extract step reads the download URL from the CKAN API rather than hardcoding a link, because the portal issues temporary download URLs.

## Tech Stack
1. Python (pandas, requests)
2. Git and GitHub for version control