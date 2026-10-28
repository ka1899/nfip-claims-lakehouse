SELECT
    CASE
        WHEN rated_flood_zone LIKE 'V%' THEN 'V - Coastal high risk'
        WHEN rated_flood_zone LIKE 'A%' THEN 'A - High risk'
        WHEN rated_flood_zone LIKE 'B%' OR rated_flood_zone LIKE 'C%' OR rated_flood_zone LIKE 'X%' THEN 'B/C/X - Moderate/Low risk'
        ELSE 'Other/unknown'
    END AS zone_group,
    COUNT(*) AS paid_claims,
    AVG(total_paid) AS avg_paid,
    AVG(payout_ratio) AS avg_payout_ratio,
    MEDIAN(payout_ratio) AS median_payout_ratio
FROM NFIP.CORE.FCT_CLAIMS
WHERE is_paid_claim
GROUP BY zone_group
ORDER BY paid_claims DESC;
