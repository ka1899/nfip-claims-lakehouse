SELECT
    COUNT(*) FILTER (WHERE amountPaidOnBuildingClaim IS NULL) AS null_rows,
    COUNT(*) FILTER (WHERE amountPaidOnBuildingClaim = '') AS empty_rows,
    COUNT(*) FILTER (
        WHERE amountPaidOnBuildingClaim IS NOT NULL
            AND amountPaidOnBuildingClaim <> ''
            AND TRY_CAST(amountPaidOnBuildingClaim AS DOUBLE) IS NULL
    ) AS unparseable_rows,
    COUNT(*) FILTER (WHERE TRY_CAST(amountPaidOnBuildingClaim AS DOUBLE) < 0) AS negative_rows,
    COUNT(*) FILTER (WHERE TRY_CAST(amountPaidOnBuildingClaim AS DOUBLE) = 0) AS zero_rows
FROM read_parquet('data/raw/FimaNfipClaims/**/*.parquet', hive_partitioning = true);
