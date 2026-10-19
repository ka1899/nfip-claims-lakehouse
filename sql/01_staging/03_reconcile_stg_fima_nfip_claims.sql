SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT id) AS distinct_ids,
    COUNT_IF(amount_paid_on_building_claim IS NULL) AS null_building_payments,
    COUNT_IF(amount_paid_on_building_claim = 0) AS zero_building_payments,
    COUNT_IF(amount_paid_on_building_claim < 0) AS neg_building_payments,
    COUNT_IF(is_negative_building_payment) AS neg_building_payments_check,
    COUNT_IF(county_code IS NULL) AS null_county_codes
FROM NFIP.STAGING.STG_FIMA_NFIP_CLAIMS;
