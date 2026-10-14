-- Load the silver Parquet export from the internal stage into staging.
-- Upload the part-*.parquet file to @NFIP.STAGING.SILVER_STAGE/fima_nfip_claims/ first (see docs/01_snowflake_load.md).
--
-- MATCH_BY_COLUMN_NAME maps Parquet columns to table columns by name, not position, so column order cannot shift data.
-- PATTERN skips Spark's _SUCCESS, _committed_* and _started_* marker files.
-- ON_ERROR = ABORT_STATEMENT loads all rows or none, so a bad file never leaves a partial table.
-- COPY remembers loaded files for 64 days and skips them on a rerun. To reload, TRUNCATE the table first.

USE ROLE SYSADMIN;
USE WAREHOUSE NFIP_WH;

COPY INTO NFIP.STAGING.STG_FIMA_NFIP_CLAIMS
FROM @NFIP.STAGING.SILVER_STAGE/fima_nfip_claims/
PATTERN = '.*[.]parquet'
FILE_FORMAT = (FORMAT_NAME = 'NFIP.STAGING.PARQUET_FMT')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
INCLUDE_METADATA = (_source_file = METADATA$FILENAME, _loaded_at = METADATA$START_SCAN_TIME)
ON_ERROR = ABORT_STATEMENT;
