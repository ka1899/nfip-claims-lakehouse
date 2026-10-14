-- One-time Snowflake setup for the NFIP lakehouse. Run top to bottom in a Snowsight worksheet.
-- Objects are owned by SYSADMIN, not ACCOUNTADMIN: ACCOUNTADMIN is for account admin, not for building tables.

USE ROLE SYSADMIN;

-- XSMALL is the smallest (1 credit/hour). Auto-suspend after 60s idle so the trial credits are not burned while idle.
CREATE WAREHOUSE IF NOT EXISTS NFIP_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

USE WAREHOUSE NFIP_WH;

CREATE DATABASE IF NOT EXISTS NFIP;

-- One schema per layer: STAGING mirrors silver as loaded, CORE holds the star schema, MARTS holds reporting tables.
CREATE SCHEMA IF NOT EXISTS NFIP.STAGING;
CREATE SCHEMA IF NOT EXISTS NFIP.CORE;
CREATE SCHEMA IF NOT EXISTS NFIP.MARTS;

-- USE_LOGICAL_TYPE reads Parquet logical types (DATE, DECIMAL) as written by Spark instead of their raw storage type.
CREATE FILE FORMAT IF NOT EXISTS NFIP.STAGING.PARQUET_FMT
    TYPE = PARQUET
    USE_LOGICAL_TYPE = TRUE;

-- Internal stage: Snowflake-managed storage, so no S3 bucket or cloud credentials are needed.
CREATE STAGE IF NOT EXISTS NFIP.STAGING.SILVER_STAGE
    FILE_FORMAT = NFIP.STAGING.PARQUET_FMT;
