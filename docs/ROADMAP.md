# Roadmap

## Why this stack
Data analyst postings most often ask for SQL plus a cloud warehouse (Snowflake is the most common name) and a BI tool. Databricks/Spark shows big data skills. This project uses Databricks for heavy processing and Snowflake as the analytics warehouse, so both appear on the resume with a clear reason for each.

## Data
OpenFEMA datasets (free, no key): FimaNfipClaims (~2M+ rows), FimaNfipPolicies (tens of millions of rows), DisasterDeclarationsSummaries.

## Phases
1. **Setup**: Snowflake trial, Databricks Free Edition, repo, environment, secrets handling.
2. **Extraction**: paginated OpenFEMA API pull, incremental loads, land as partitioned Parquet.
3. **Big data processing (Databricks)**: bronze (raw Delta), silver (cleaned, typed, deduped), partitioning by year/state, broadcast joins, Z-ordering, file compaction, before/after performance notes.
4. **Warehouse (Snowflake)**: load via stage + COPY INTO, star schema (fact_claims, fact_policies, dim_date, dim_geography, dim_building, dim_flood_zone).
5. **SQL analysis (written by you)**: CTEs, window functions, cohort/trend analysis, loss ratios, percentile durations, query optimization with EXPLAIN/query profile. Each query documented against a business question.
6. **Data quality**: row counts, null/uniqueness checks, reconciliation between layers.
7. **Dashboard**: KPIs, state map, loss trends, segment drill-downs.
8. **Polish**: README with screenshots, architecture diagram, resume bullets, short demo video.

## Working agreement
You write the SQL. Claude Code scaffolds, explains, reviews, and suggests optimizations.
