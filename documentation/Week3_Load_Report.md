# Week 3 Load Report - SCMD

## Summary
- Loaded 310,344 fact rows for 202605 into a SQLite star-schema warehouse (data/warehouse/scmd.db).
- Engine: SQLite (zero setup, single portable file, sufficient for one month of SCMD data).
- Idempotency proven: running the load (and the full pipeline) twice leaves the fact table at
  exactly 310,344 rows, no duplication.

## Schema
See docs/Week3_Schema_Design.md for the full star schema, ERD, and table definitions.
- Fact: fact_medicines_issued (grain: one Trust x Medicine x Month)
- Dimensions: dim_trust, dim_medicine, dim_date

## Task 3.0 Reconciliation
My Week 2 Parquet had the source header typo TOTAL_QUANITY_IN_VMP_UNIT and lacked separate
year/month columns. I fixed both at the source (standardize_columns step in src/transform.py:
renamed to TOTAL_QUANTITY_IN_VMP_UNIT and derived year/month), then regenerated the Parquet.
Final row count 310,344 (my own cleaning decisions; differs from the spec's illustrative 311,072).

## Key Decisions and Trade-offs

### Database engine: SQLite vs PostgreSQL
- Choice: SQLite.
- Reasoning: no server to manage, single file, enough for one laptop's monthly data.
- Impact: not suited to concurrent writers or a shared server; would move to Postgres if that need arises.

### Fact load: delete-and-insert vs row-by-row upsert
- Choice: delete-and-insert by month partition (delete this month's rows, insert fresh, in one transaction).
- Reasoning: each load is a full month's snapshot from one Parquet file; there is never a reason to
  mix old and new rows for the same month. Simpler to reason about and equally idempotent.
- Impact: would switch to a row-level upsert if I ever loaded partial-month updates.

### Orchestration: cron/Task Scheduler vs Airflow
- Choice: run via a single command (src/pipeline.py), scheduled via Windows Task Scheduler,
  evidenced by logs/pipeline.log.
- Reasoning: a monthly batch job does not justify Airflow's overhead. Boring technology first.
- Impact: would adopt Airflow only for retries with backoff, cross-pipeline dependencies, or a UI.

## Quality Gates
Two gates wired into src/pipeline.py:
1. Row-count gate (before load): halts if the processed file has fewer than 280,000 rows
   (guards against silent upstream data loss). On the good run: PASSED at 310,344 rows.
2. Referential integrity gate (after load): halts if any fact row references a trust, medicine,
   or date not present in the dimensions. On the good run: PASSED (0 orphaned rows).

Failure demo: pointing the row-count gate at a deliberately truncated 10-row file produced
"FAILED: row count gate - 10 rows (expected >= 280,000)" and returned False, proving the gate
stops bad data rather than loading it. Evidence in logs/gate_failure_demo.log.

## Monitoring (current vs future)
Current: the pipeline exits non-zero on a gate failure, with a clear log line, captured in
logs/pipeline.log. That is a legitimate baseline for a monthly student pipeline.
Future: at production scale I would add a webhook/Slack alert in the pipeline's except block so a
failure notifies a human, and capture run metrics (rows loaded, duration) for trend monitoring.
