# Loading silver into Snowflake staging

Path: Databricks Volume export (one Parquet file) -> local `data/silver/` -> Snowflake internal stage -> `NFIP.STAGING.STG_FIMA_NFIP_CLAIMS`.

SQL files are in `sql/01_staging/`, run in order.

## Steps

1. **Trial account.** Sign up for a Snowflake trial (Standard edition, AWS). Do this yourself; never paste passwords or codes into chat.
2. **Setup** (`00_setup.sql`). Creates warehouse `NFIP_WH` (XSMALL, auto-suspend 60s), database `NFIP` with schemas `STAGING`, `CORE`, `MARTS`, a Parquet file format, and an internal stage. Every statement is `IF NOT EXISTS`, so rerunning is safe.
3. **Table** (`01_create_stg_fima_nfip_claims.sql`). 30 silver columns plus 2 lineage columns.
4. **Download** the `part-00000-*.parquet` file from `/Volumes/workspace/silver/exports/fima_nfip_claims/` in Databricks into `data/silver/fima_nfip_claims/` (gitignored). Skip the `_SUCCESS`, `_committed_*` and `_started_*` files. Note the file size.
5. **Upload** to the stage in Snowsight: Catalog, `NFIP`, `STAGING`, Stages, `SILVER_STAGE`, then **+ Files**, with path `fima_nfip_claims`. Snowsight uploads are capped at 250 MB per file. If the file is bigger, re-export from Databricks with `.repartition(4)` instead of `.coalesce(1)`, or upload with `PUT` from the Snowflake CLI.
6. **Load** (`02_copy_stg_fima_nfip_claims.sql`). The result grid shows one row per file with `rows_loaded` and `errors_seen`.

## Expected after load (reconcile against silver)

| Check | Expected |
|-------|----------|
| Row count | 2,721,780 |
| Distinct `id` | 2,721,780 |
| `amount_paid_on_building_claim` NULL | 566,351 |
| `amount_paid_on_building_claim` = 0 | 150,348 |
| `is_negative_building_payment` true | 86 |
| `county_code` NULL | 62,442 |

Silver to staging should change no counts. Any difference means the load, not the data, is wrong.

## Design choices

- **Internal stage, not S3.** No cloud bucket or IAM setup; enough for a one-off load of a few hundred MB.
- **`MATCH_BY_COLUMN_NAME`.** Columns are matched by name, so a column order change in silver cannot silently shift values into the wrong column.
- **`NUMBER(18,2)` for money.** Exact decimals, same as silver's `DECIMAL(18,2)`. FLOAT would introduce rounding in sums.
- **Codes as VARCHAR.** County, zip and census tract codes have leading zeros that a numeric type would drop.
- **`ON_ERROR = ABORT_STATEMENT`.** All or nothing; no partial loads to clean up.
- **Lineage columns.** `_source_file` and `_loaded_at` record where and when each row was loaded, which helps reconciliation and debugging.
- **SYSADMIN owns the objects.** ACCOUNTADMIN is kept for account administration, which is Snowflake's recommended practice.
