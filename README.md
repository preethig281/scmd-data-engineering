# Architecture

## Overview
<One or two sentences describing the pipeline approach — this is an ELT
pipeline: Extract raw CSV from NHSBSA, Load it, Transform into clean tables.>

## Data Flow
1. **Extract** — download the monthly SCMD CSV from the NHSBSA Open Data Portal (`src/extract.py`)
2. **Validate** — check row counts, nulls, types, duplicates (`src/validate.py`)
3. **Transform** — clean and standardise (fix types, handle the QUANITY column, etc.) (`src/transform.py`)
4. **Load** — write processed data to `data/processed/` (`src/load.py`)

## Key Design Decisions
- Raw data kept out of git (large, re-downloadable) — see `.gitignore`
- SNOMED and ODS codes handled as text to avoid numeric corruption
- <add one more as you think of it>

## Tech Stack
- Python