SELECT COUNT(*) AS total_rows
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true);
