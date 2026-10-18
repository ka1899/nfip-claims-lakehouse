-- Staging table for FEMA disaster declarations (one row per declared area per disaster).
-- Built by ingestion/prepare_disasters.py; columns mirror that Parquet file so COPY can match by name.
-- fips_county_code '000' means the declaration covers the whole state.

CREATE OR REPLACE TABLE NFIP.STAGING.STG_DISASTER_DECLARATIONS (
    id                      VARCHAR NOT NULL,
    disaster_number         VARCHAR,
    fema_declaration_string VARCHAR,
    state                   VARCHAR,
    fips_state_code         VARCHAR,
    fips_county_code        VARCHAR,
    designated_area         VARCHAR,
    declaration_type        VARCHAR,  -- DR major disaster, EM emergency, FM fire management
    declaration_title       VARCHAR,
    incident_type           VARCHAR,
    declaration_date        DATE,
    incident_begin_date     DATE,
    incident_end_date       DATE,
    fy_declared             INTEGER,
    _source_file            VARCHAR,
    _loaded_at              TIMESTAMP_LTZ
);
