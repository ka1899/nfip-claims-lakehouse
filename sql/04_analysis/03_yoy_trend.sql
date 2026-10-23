WITH yearly AS (
    SELECT
        year_of_loss,
        COUNT(*) AS claim_count,
        SUM(total_paid) AS total_paid
    FROM NFIP.CORE.FCT_CLAIMS
    WHERE is_complete_year
    GROUP BY year_of_loss
)
SELECT 
    year_of_loss,
    claim_count,
    total_paid,
    LAG(total_paid) OVER(ORDER BY year_of_loss) AS prev_year_paid,
    ROUND((total_paid - prev_year_paid) / NULLIF(prev_year_paid,0) * 100,1) AS yoy_percent_change
FROM yearly
ORDER BY year_of_loss;
