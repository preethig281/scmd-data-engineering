# Pipeline Runbook - SCMD

## Quick Start

Run the full transform pipeline with one command:

Output: data/processed/scmd_202605_processed.parquet

## Steps

### Step 1: Extract (run separately)
- Downloads the SCMD CSV from the NHSBSA portal via the CKAN API.
- Saves to data/raw/scmd_provisional_202605.csv (about 35 MB).
- Verifies the downloaded size against the size the API reports.

### Step 2: Transform + Validate
- Downloads the SCMD CSV from the NHSBSA portal via the CKAN API.
- Saves to data/raw/scmd_provisional_202605.csv (about 35 MB).
- Verifies the downloaded size against the size the API reports.

### Step 2: Transform + Validate


Run with coverage:


## Common Issues

### "FileNotFoundError: data/raw/scmd_provisional_202605.csv"
- The raw file is missing. Run the extract step first: python src/extract.py

### "ModuleNotFoundError: No module named 'pandas'" (or pyarrow, pytest)
- Install the dependencies:


### Download fails or returns an error
- The NHSBSA portal may be temporarily down. Check https://opendata.nhsbsa.net and try again.

## Notes
- Raw and processed data are not committed to git (see .gitignore); they are re-creatable by running the pipeline.
- Processed output is Parquet: smaller, faster to query, and it preserves data types.
