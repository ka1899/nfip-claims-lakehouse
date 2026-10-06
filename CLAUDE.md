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
Phase 1 (setup) not started: Snowflake trial, Databricks Free Edition, Python env, secrets handling.
