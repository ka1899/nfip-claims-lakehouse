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

## Current status
Phase 1 (setup) in progress.
- Done: Python env, ingestion/extract_openfema.py (paginated, resumable, partitioned Parquet), FimaNfipClaims pulled locally to data/raw (2,721,780 rows, ~13,377 files, all columns strings), DuckDB CLI installed, Databricks Free Edition signed up, schemas workspace.bronze and workspace.silver created, Volume workspace.bronze.raw_files created, FimaNfipClaims zip uploaded and unzipped there (took ~22 min for ~13k small files), Spark row count in Databricks = 2,721,780 (matches API count), 74 columns. Baseline timings in docs/03_performance_notes.md. Bronze Delta table workspace.bronze.fima_nfip_claims written by spark/01_bronze_claims.py (unpartitioned, all strings), row count reconciled to 2,721,780.
- Next: record bronze numFiles, then Phase 3 silver (types, dedup) and the compaction / partitioning experiments with before/after timings. .env secrets handling when a credential is needed.
- Not started: Snowflake trial (start it just before Phase 4), .env secrets handling.
- Learner mode: Khushi does account actions herself and pastes on-screen text; explain the why of each step; never ask for secrets in chat.
