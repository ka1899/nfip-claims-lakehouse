SELECT
    SUM(CASE WHEN amountPaidOnBuildingClaim IS NULL THEN 1 ELSE 0 END) AS no_of_null_rows,
    SUM(CASE WHEN amountPaidOnBuildingClaim ='' THEN 1 ELSE 0 END) AS no_of_empty_rows,
    MIN(TRY_CAST(amountPaidOnBuildingClaim AS DOUBLE)) AS min_amount,
    MAX(TRY_CAST(amountPaidOnBuildingClaim AS DOUBLE)) AS max_amount
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true);

