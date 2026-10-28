WITH state_months AS (
    SELECT
        state,
        DATE_TRUNC('MONTH', date_of_loss) AS loss_month,
        COUNT(*) AS claim_count,
        SUM(total_paid) AS total_paid
    FROM NFIP.CORE.FCT_CLAIMS
    WHERE is_complete_year
    GROUP BY state, loss_month
),
declared AS(
    SELECT
        state,
        DATE_TRUNC('month', incident_begin_date) AS begin_month,
        LISTAGG(DISTINCT declaration_title, '; ') AS disasters
    FROM NFIP.STAGING.STG_DISASTER_DECLARATIONS AS disaster_table
    WHERE incident_type IN ('Flood', 'Hurricane', 'Severe Storm', 'Tropical Storm', 'Coastal Storm', 'Typhoon', 'Dam/Levee Break', 'Tropical Depression')
    GROUP BY state, begin_month
)
SELECT
    sm.state,
    sm.loss_month,
    disasters,
    claim_count,
    total_paid
FROM state_months sm
LEFT JOIN declared d ON sm.state = d.state AND d.begin_month = sm.loss_month
ORDER BY total_paid DESC
LIMIT 20;
