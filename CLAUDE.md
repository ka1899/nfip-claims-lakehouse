# CLAUDE.md

## Project
NFIP Flood Insurance Claims Lakehouse: an end-to-end analytics pipeline built as a portfolio project for data analyst roles (insurance/banking risk analytics focus). Owner: Khushi Advani (Columbia MS Data Science, graduating Dec 2026).

Pipeline: OpenFEMA API -> Python ingestion -> Parquet -> Databricks (PySpark + Delta, bronze/silver) -> Snowflake (staging -> core -> marts) -> dashboard.

Datasets (OpenFEMA, free, no key): FimaNfipClaims, FimaNfipPolicies, DisasterDeclarationsSummaries.

See README.md for business questions and docs/ROADMAP.md for the phased plan.

## Working agreement (important)
- Khushi writes the analytical SQL herself. The goal is genuine, hand-written, optimized SQL she can defend in interviews.
- Claude scaffolds, explains, reviews, and suggests optimizations. Do NOT write the analysis queries in sql/04_analysis for her. Give the business question, hints, expected output shape, and review her attempt.
- Claude may write boilerplate: ingestion scripts, Spark jobs, DDL for staging, CI, dashboard shell, data quality test harness. Explain choices briefly so she can talk about them.
- Document every query against a business question in docs/.

## Conventions
- Snowflake SQL, uppercase keywords, snake_case, one query per file, numbered by layer folder.
- Never commit secrets or raw data. Credentials via .env (gitignored). Data lives in data/ (gitignored).
- Commit small and often, with clear messages.

## Current status (updated 2026-10-14)
Goal: a resume-worthy end-to-end project by Sunday 2026-10-18. Scope is trimmed (see Plan).

Done
- Extraction: ingestion/extract_openfema.py (paginated, resumable, idempotent, partitioned Parquet). FimaNfipClaims: 2,721,780 rows, matches API count.
- Databricks Free Edition: schemas workspace.bronze and workspace.silver, Volume workspace.bronze.raw_files, bronze Delta table workspace.bronze.fima_nfip_claims (spark/01_bronze_claims.py, 9 files, 2,721,780 rows, all strings).
- Baseline vs bronze timings in docs/03_performance_notes.md (raw ~13.4k files vs 9 Delta files, first-run speedup ~5.8x count and ~2.6x group by).
- Khushi's raw profiling queries sql/00_profiling/01 to 07 and docs/00_profiling.md (hers; review, do not rewrite).
- Silver notebook written: spark/02_silver_claims.py (29 kept columns, snake_case, DECIMAL(18,2) money, blanks to NULL, negative-payment flag, export to Volume workspace.silver.exports). Cast check passed (no values lost, no money rounding). Khushi was running the remaining cells (write, reconcile, export) in Databricks; confirm silver row count = 2,721,780.

Decisions made
- One branch: work on main (the old claude/... branch can be deleted). Push to main.
- Money is DECIMAL(18,2); keep NULL distinct from 0; keep the 86 negative building payments (flagged, not clamped).
- Unpartitioned bronze first; partitioning/OPTIMIZE experiments are optional extras.

Known gaps (say so honestly in the README)
- Claims data has no claim close date and no premium column, so README Q3 (time to close) and Q4 (underpriced segments) cannot be answered from claims alone. Cut or replace them.
- Open items from profiling: prove amountPaidOnBuildingClaim has no unparseable values with COUNT(col) vs COUNT(TRY_CAST); save the query behind "150,348 rows exactly 0"; investigate the 10.7M maximum payment; profile the other 11 indicator columns.

Plan to Sunday
1. Wed/Thu: finish silver and export; start Snowflake trial (Standard, AWS), warehouse XSMALL auto-suspend 60s; load silver Parquet via PUT + COPY INTO to staging; core/star schema DDL (Claude scaffolds DDL; Khushi writes the transformation SQL).
2. Thu/Fri: extract DisasterDeclarationsSummaries with the same script (for Q5).
3. Fri/Sat: Khushi writes 5 or 6 analysis queries (Q1 loss by state/county over time, Q2 payout ratios by segment, Q5 spikes vs declarations), documented in docs/; Claude reviews. Data quality test harness and Streamlit dashboard shell by Claude.
4. Sun: README with screenshots, architecture diagram, resume bullets.

Cut for now: FimaNfipPolicies, incremental loads, extra performance experiments.

Open question: Snowflake trial not yet confirmed started.

## Learner mode
- Khushi does account actions herself (Snowflake, Databricks) and never pastes passwords, tokens or codes into chat. Credentials go in .env (gitignored); show only variable names.
- Explain the why of each step briefly. Prefer bigger chunks over one tiny step at a time; she wants speed.
- No em dashes in any text.
- Environment note: a cloud session cannot reach fema.gov. A local session on her Mac can run the extractor, DuckDB, git and the Databricks/Snowflake CLIs.
