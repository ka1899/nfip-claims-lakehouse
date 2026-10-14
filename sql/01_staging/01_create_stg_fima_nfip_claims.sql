-- Staging table for silver FimaNfipClaims (workspace.silver.fima_nfip_claims in Databricks).
-- Columns and types mirror silver one to one, so COPY can match them by name.
-- Codes stay VARCHAR (leading zeros in county, zip, tract). Money is NUMBER(18,2), never FLOAT.

CREATE OR REPLACE TABLE NFIP.STAGING.STG_FIMA_NFIP_CLAIMS (
    id                                                VARCHAR NOT NULL,  -- Snowflake enforces NOT NULL, but not PRIMARY KEY or UNIQUE
    state                                             VARCHAR,
    county_code                                       VARCHAR,
    reported_zip_code                                 VARCHAR,
    census_tract                                      VARCHAR,
    flood_zone_current                                VARCHAR,
    rated_flood_zone                                  VARCHAR,
    occupancy_type                                    VARCHAR,
    building_description_code                         VARCHAR,
    cause_of_damage                                   VARCHAR,
    flood_event                                       VARCHAR,
    event_designation_number                          VARCHAR,
    nfip_community_name                               VARCHAR,
    date_of_loss                                      DATE,
    original_construction_date                        DATE,
    primary_residence_indicator                       BOOLEAN,
    post_firm_construction_indicator                  BOOLEAN,
    latitude                                          FLOAT,
    longitude                                         FLOAT,
    year_of_loss                                      INTEGER,
    amount_paid_on_building_claim                     NUMBER(18,2),
    amount_paid_on_contents_claim                     NUMBER(18,2),
    amount_paid_on_increased_cost_of_compliance_claim NUMBER(18,2),
    total_building_insurance_coverage                 NUMBER(18,2),
    total_contents_insurance_coverage                 NUMBER(18,2),
    building_damage_amount                            NUMBER(18,2),
    contents_damage_amount                            NUMBER(18,2),
    building_property_value                           NUMBER(18,2),
    building_replacement_cost                         NUMBER(18,2),
    is_negative_building_payment                      BOOLEAN,
    -- Load lineage, filled by COPY INTO (INCLUDE_METADATA): which file each row came from, and when.
    _source_file                                      VARCHAR,
    _loaded_at                                        TIMESTAMP_LTZ
);
