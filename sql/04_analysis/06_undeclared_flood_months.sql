WITH state_months AS (
    SELECT
        state,
        DATE_TRUNC('MONTH', date_of_loss) AS loss_month,
        COUNT(*) AS claim_count,
        SUM(total_paid) AS total_paid
    FROM NFIP.CORE.FCT_CLAIMS
    WHERE is_complete_year
    GROUP BY state, loss_month
)
SELECT
    sm.state,
    sm.loss_month,
    claim_count,
    total_paid
FROM state_months sm
WHERE NOT EXISTS (
    SELECT 1
    FROM NFIP.STAGING.STG_DISASTER_DECLARATIONS dd
    WHERE dd.state = sm.state
      AND dd.incident_type IN ('Flood', 'Hurricane', 'Severe Storm', 'Tropical Storm', 'Coastal Storm', 'Typhoon', 'Dam/Levee Break', 'Tropical Depression')
      AND sm.loss_month BETWEEN DATE_TRUNC('month', dd.incident_begin_date)
                            AND DATE_TRUNC('month', COALESCE(dd.incident_end_date,dd.incident_begin_date))
)
ORDER BY total_paid DESC
LIMIT 10;
