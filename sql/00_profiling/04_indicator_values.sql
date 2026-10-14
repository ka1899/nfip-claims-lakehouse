SELECT 
    CASE 
        WHEN primaryResidenceIndicator IS NULL THEN '(null)'
        WHEN primaryResidenceIndicator = '' THEN '(empty)'
        ELSE primaryResidenceIndicator
    END AS distinct_indicators,
    COUNT(*) AS indicator_count
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true)
GROUP BY distinct_indicators
ORDER BY indicator_count DESC;