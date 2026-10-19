CREATE OR REPLACE VIEW NFIP.CORE.FCT_CLAIMS AS
SELECT
    id,
    state,
    county_code,
    rated_flood_zone,
    occupancy_type,
    date_of_loss,
    year_of_loss,
    is_negative_building_payment,
    COALESCE(amount_paid_on_building_claim, 0) +  
        COALESCE(amount_paid_on_contents_claim, 0) + 
            COALESCE(amount_paid_on_increased_cost_of_compliance_claim, 0) AS total_paid,
    COALESCE(total_building_insurance_coverage, 0) + COALESCE(total_contents_insurance_coverage,0) AS total_coverage,
    total_paid / NULLIF(total_coverage,0) AS payout_ratio,
    (total_paid > 0) AS is_paid_claim,
    (year_of_loss < 2025) AS is_complete_year,
    FLOOR(year_of_loss/10)*10 AS loss_decade
FROM NFIP.STAGING.STG_FIMA_NFIP_CLAIMS;
