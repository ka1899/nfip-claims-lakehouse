SELECT
    COUNT_IF(amount_paid_on_building_claim IS NULL) AS null_building_payments,
    COUNT_IF(amount_paid_on_building_claim < 0) AS negative_building_payments,
    COUNT_IF(amount_paid_on_building_claim = 0) AS zero_building_payments,
    COUNT_IF(is_negative_building_payment = TRUE) AS negative_building_payments_check
FROM 
    workspace.silver.fima_nfip_claims
