WITH county_totals AS (
    SELECT SUM(total_paid) AS county_paid, county_code, state
    FROM NFIP.CORE.FCT_CLAIMS
    WHERE county_code IS NOT NULL
    GROUP BY county_code, state
),
running AS (
    SELECT
        state,
        county_code,
        county_paid,
        SUM(county_paid) OVER (ORDER BY county_paid DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / SUM(county_paid) OVER ()           AS cum_share
            
    FROM county_totals
) 
SELECT
    COUNT(*) AS total_counties,
    COUNT_IF(cum_share<0.8) AS counties_for_80_pct,
    counties_for_80_pct / total_counties AS pct_of_counties
    FROM running;
