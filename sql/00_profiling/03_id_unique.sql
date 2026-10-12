SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT id) AS distinct_ids
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true);