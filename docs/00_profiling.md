# Raw-layer profiling: FimaNfipClaims

Run dates: 2026-10-12 (queries 1 to 3) and 2026-10-14 (queries 4 to 7). Engine: DuckDB, reading the raw Parquet directly (`data/raw/FimaNfipClaims/`, Hive-partitioned by `yearOfLoss`). Queries are in `sql/00_profiling/`.

Purpose: confirm the extraction landed the whole dataset, once, before building any layer on top of it.

| # | Query | Business question | Result |
|---|-------|-------------------|--------|
| 1 | `01_row_count.sql` | Did we land every claim the API reported? | 2,721,780 rows, equal to the API's `$count` |
| 2 | `02_rows_per_year.sql` | How are claims spread over time, and is any claim missing a loss year? | 49 years (1978 to 2026), no `unknown` partition |
| 3 | `03_id_unique.sql` | Is `id` unique, so one row is one claim? | 2,721,780 rows and 2,721,780 distinct ids |
| 4 | `04_indicator_values.sql` | What values does `primaryResidenceIndicator` hold, and are any missing? | `false` 1,383,455 and `true` 1,338,325; no NULLs or empty strings |
| 5 | `05_building_claim_amount.sql` | How many building payments are missing, and what range do the real values span? | 566,351 NULL, 0 empty; min -201,667.50, max 10,741,476.93 |
| 6 | `06_negative_building_payments.sql` | Which claims have a negative building payment? | 86 rows, from -34.94 to -201,667.50 |
| 7 | `07_date_of_loss_parse.sql` | Does every `dateOfLoss` value parse as a date? | 2,721,780 non-NULL values, all 2,721,780 parse |

## Findings

- **Completeness:** landed rows equal the source count. This is the first source-to-bronze reconciliation check for Phase 6.
- **Uniqueness:** `id` has no duplicates, so paging with `$orderby=id` and `$skip` did not skip or repeat rows. It also has no missing values, since a missing id would have made the two counts differ.
- **Loss years:** every row has a `yearOfLoss`. This was confirmed three ways: no `unknown` row in query 2, DuckDB read the partition column as a number, and no `yearOfLoss=unknown` folder exists on disk.
- **Spikes:** the largest years are 2005 (277,027), 2012 (175,804), 2017 (145,681), 2008 (96,968) and 2011 (96,466). These match well-known hurricane years (Katrina, Sandy, Harvey/Irma, Ike, Irene), but that link comes from general knowledge and has not been checked against the data, for example by looking at state or disaster fields.
- **Incomplete years:** 2025 (13,114) and 2026 (2,078) are low because the years are not finished, and claims are still being filed. Trend analysis must flag or exclude them.
- **Indicator flags:** `primaryResidenceIndicator` is a clean `true`/`false` column (about 51% `false`, 49% `true`) and can be cast straight to a boolean in silver. I read `false` as "not the owner's main home", but that comes from the column name and has not been checked against the FEMA data dictionary. Only this one indicator was profiled; the other 11 indicator columns have not been checked.
- **Building payments:** 566,351 rows (about 21%) have a NULL `amountPaidOnBuildingClaim`. There are no empty strings and no unparseable values. 150,348 rows are exactly 0, which is a real value and must stay distinct from NULL in silver.
- **Negative payments:** 86 rows have a negative building payment. The most negative are recent (2024, 2024, 2022), and several are round numbers such as -5,000.00. They may be refunds, recoveries or corrections, but that is a guess; nothing in the data confirms it yet.
- **Very large payment:** the maximum is 10,741,476.93, which looks high for one building claim. From memory, NFIP building coverage is capped at $250,000 (residential) and $500,000 (non-residential); that figure has not been verified against FEMA documentation. Check these rows before using the amounts in loss analysis.
- **Loss dates:** all 2,721,780 `dateOfLoss` values are present and parse as dates in DuckDB, so no special handling is needed for this column. DuckDB and Snowflake may accept different date formats, so this check should be repeated in Snowflake.

## Not yet verified

- The 49 yearly counts were not summed to confirm they total 2,721,780. This should hold, since `GROUP BY` puts each row in exactly one group.
- Null and empty values have been profiled only for `id`, `yearOfLoss`, `primaryResidenceIndicator`, `amountPaidOnBuildingClaim` and `dateOfLoss`. The remaining columns are planned for silver (Phase 3) and the Phase 6 data quality checks.
- The 86 negative payments and the 10.7M maximum have not been investigated beyond listing them.

## Notes for later layers

- DuckDB reads the partition column as an integer, but the raw files store every column as a string. Types are set explicitly in silver.
- The raw folder holds about 13,377 small Parquet files (689 MB). File compaction in Phase 3 is the fix, with before/after timings.
- `_checkpoint.json` sits inside the dataset folder. Read only `*.parquet` files, or remove it, when loading in Spark.
