# NFIP Flood Insurance Claims Lakehouse

End-to-end analytics pipeline on FEMA's National Flood Insurance Program (NFIP) data: API extraction, Spark processing on Databricks, a Snowflake warehouse with hand-written SQL, and a dashboard.

**Status:** planning. See [docs/ROADMAP.md](docs/ROADMAP.md).

## Business questions
1. Which states and counties drive the largest flood losses, and how has that shifted over time?
2. How do payout ratios (paid vs. coverage) vary by building type, flood zone, and occupancy?
3. How long do claims take to close, and which segments are slowest?
4. Which policy segments look underpriced (premium vs. paid loss)?
5. How do loss spikes line up with named storms and disaster declarations?

## Architecture
```
OpenFEMA API -> Python ingestion -> Parquet (raw) -> Databricks (PySpark + Delta, bronze/silver)
             -> Snowflake (staging -> core -> marts, SQL + dbt-style layering) -> Dashboard
```

## Stack
Python, PySpark, Delta Lake, Databricks (Free Edition), Snowflake (trial), SQL, Streamlit (or Power BI/Tableau), GitHub Actions.

## Repo layout
- `ingestion/` API extraction scripts
- `spark/` PySpark / Spark SQL notebooks and jobs
- `sql/` Snowflake SQL by layer (staging, core, marts, analysis)
- `dashboard/` dashboard app
- `docs/` roadmap, data dictionary, design decisions
- `tests/` data quality checks
