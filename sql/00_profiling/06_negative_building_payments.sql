SELECT
    id,
    yearOfLoss,
    TRY_CAST(amountPaidOnBuildingClaim AS DOUBLE) AS negative_amount
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true)
WHERE TRY_CAST(amountPaidOnBuildingClaim AS DOUBLE) < 0
ORDER BY negative_amount ASC;