# Raw-layer profiling: FimaNfipClaims

Run date: 2026-10-12. Engine: DuckDB, reading the raw Parquet directly (`data/raw/FimaNfipClaims/`, Hive-partitioned by `yearOfLoss`). Queries are in `sql/00_profiling/`.

Purpose: confirm the extraction landed the whole dataset, once, before building any layer on top of it.

| # | Query | Business question | Result |
|---|-------|-------------------|--------|
| 1 | `01_row_count.sql` | Did we land every claim the API reported? | 2,721,780 rows, equal to the API's `$count` |
| 2 | `02_rows_per_year.sql` | How are claims spread over time, and is any claim missing a loss year? | 49 years (1978 to 2026), no `unknown` partition |
| 3 | `03_id_unique.sql` | Is `id` unique, so one row is one claim? | 2,721,780 rows and 2,721,780 distinct ids |

## Findings

- **Completeness:** landed rows equal the source count. This is the first source-to-bronze reconciliation check for Phase 6.
- **Uniqueness:** `id` has no duplicates, so paging with `$orderby=id` and `$skip` did not skip or repeat rows. It also has no missing values, since a missing id would have made the two counts differ.
- **Loss years:** every row has a `yearOfLoss`. This was confirmed three ways: no `unknown` row in query 2, DuckDB read the partition column as a number, and no `yearOfLoss=unknown` folder exists on disk.
- **Spikes:** the largest years are 2005 (277,027), 2012 (175,804), 2017 (145,681), 2008 (96,968) and 2011 (96,466). These match well-known hurricane years (Katrina, Sandy, Harvey/Irma, Ike, Irene), but that link comes from general knowledge and has not been checked against the data, for example by looking at state or disaster fields.
- **Incomplete years:** 2025 (13,114) and 2026 (2,078) are low because the years are not finished, and claims are still being filed. Trend analysis must flag or exclude them.

## Not yet verified

- The 49 yearly counts were not summed to confirm they total 2,721,780. This should hold, since `GROUP BY` puts each row in exactly one group.
- Null and empty values in columns other than `id` and `yearOfLoss` have not been profiled. This is planned for silver (Phase 3) and the Phase 6 data quality checks.

## Notes for later layers

- DuckDB reads the partition column as an integer, but the raw files store every column as a string. Types are set explicitly in silver.
- The raw folder holds about 13,377 small Parquet files (689 MB). File compaction in Phase 3 is the fix, with before/after timings.
- `_checkpoint.json` sits inside the dataset folder. Read only `*.parquet` files, or remove it, when loading in Spark.
