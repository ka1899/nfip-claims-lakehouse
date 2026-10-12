SELECT 
    yearOfLoss AS year_of_loss,
    COUNT(*) AS claim_count
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true)
GROUP BY yearOfLoss
ORDER BY yearOfLoss;