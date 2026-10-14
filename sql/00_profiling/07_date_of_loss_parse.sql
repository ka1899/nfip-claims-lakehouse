SELECT
    COUNT(dateOfLoss) AS no_of_loss,
    COUNT(TRY_CAST(dateOfLoss AS DATE)) AS parsed_no_of_loss
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true);