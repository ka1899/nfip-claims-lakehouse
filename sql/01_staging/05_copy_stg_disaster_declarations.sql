-- Load disaster declarations from the internal stage. Same options as the claims COPY (02).
-- Upload disaster_declarations.parquet to @NFIP.STAGING.SILVER_STAGE/disaster_declarations/ first.

USE ROLE SYSADMIN;
USE WAREHOUSE NFIP_WH;

COPY INTO NFIP.STAGING.STG_DISASTER_DECLARATIONS
FROM @NFIP.STAGING.SILVER_STAGE/disaster_declarations/
PATTERN = '.*[.]parquet'
FILE_FORMAT = (FORMAT_NAME = 'NFIP.STAGING.PARQUET_FMT')
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
INCLUDE_METADATA = (_source_file = METADATA$FILENAME, _loaded_at = METADATA$START_SCAN_TIME)
ON_ERROR = ABORT_STATEMENT;
