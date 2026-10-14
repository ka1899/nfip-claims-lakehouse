# Databricks notebook source
# MAGIC %md
# MAGIC # Silver: FimaNfipClaims
# MAGIC `workspace.bronze.fima_nfip_claims` -> `workspace.silver.fima_nfip_claims`.
# MAGIC
# MAGIC What silver does that bronze does not:
# MAGIC - keeps only the columns the business questions need
# MAGIC - turns blank strings into NULL
# MAGIC - casts to real types (dates, DECIMAL money, booleans)
# MAGIC - renames columns to snake_case (matches the Snowflake conventions)
# MAGIC - guards against duplicate ids
# MAGIC
# MAGIC Casts use `try_cast`, which returns NULL on a bad value instead of failing. A check cell then proves no real value was silently lost.

# COMMAND ----------

import re
from pyspark.sql import functions as F

BRONZE = "workspace.bronze.fima_nfip_claims"
SILVER = "workspace.silver.fima_nfip_claims"
EXPORT_DIR = "/Volumes/workspace/silver/exports/fima_nfip_claims"

# Edit these lists to change what silver keeps.
STRING_COLS = [
    "id", "state", "countyCode", "reportedZipCode", "censusTract",  # codes stay strings: leading zeros matter
    "floodZoneCurrent", "ratedFloodZone", "occupancyType", "buildingDescriptionCode",
    "causeOfDamage", "floodEvent", "eventDesignationNumber", "nfipCommunityName",
]
DATE_COLS = ["dateOfLoss", "originalConstructionDate"]
BOOL_COLS = ["primaryResidenceIndicator", "postFIRMConstructionIndicator"]
DOUBLE_COLS = ["latitude", "longitude"]
INT_COLS = ["yearOfLoss"]
MONEY_COLS = [  # DECIMAL(18,2): money should not use floating point
    "amountPaidOnBuildingClaim", "amountPaidOnContentsClaim", "amountPaidOnIncreasedCostOfComplianceClaim",
    "totalBuildingInsuranceCoverage", "totalContentsInsuranceCoverage",
    "buildingDamageAmount", "contentsDamageAmount", "buildingPropertyValue", "buildingReplacementCost",
]
ALL_COLS = STRING_COLS + DATE_COLS + BOOL_COLS + DOUBLE_COLS + INT_COLS + MONEY_COLS


def snake(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    return s.lower()


# COMMAND ----------

# Step 1: select kept columns, trim, and turn blank strings into NULL.
bronze = spark.table(BRONZE)
bronze_rows = bronze.count()
df0 = bronze.select([F.expr(f"nullif(trim(`{c}`), '')").alias(c) for c in ALL_COLS])

# COMMAND ----------

# Step 2: define casts (try_cast: NULL instead of an error on a value that does not parse).
casts = {}
for c in DATE_COLS:
    casts[c] = f"try_cast(substring(`{c}`, 1, 10) AS DATE)"  # takes the yyyy-MM-dd part
for c in BOOL_COLS:
    casts[c] = f"try_cast(`{c}` AS BOOLEAN)"
for c in DOUBLE_COLS:
    casts[c] = f"try_cast(`{c}` AS DOUBLE)"
for c in INT_COLS:
    casts[c] = f"try_cast(`{c}` AS INT)"
for c in MONEY_COLS:
    casts[c] = f"try_cast(`{c}` AS DECIMAL(18,2))"

# COMMAND ----------

# Step 3: prove the casts lost nothing. For every cast column, the count of non-NULL values
# must be identical before and after. A difference means some real values did not parse.
aggs = []
for c, e in casts.items():
    aggs.append(F.count(F.col(f"`{c}`")).alias(f"{c}__before"))
    aggs.append(F.count(F.expr(e)).alias(f"{c}__after"))
first_row = df0.agg(*aggs).first()
assert first_row is not None, "bronze is empty"
counts = first_row.asDict()

failures = {c: (counts[f"{c}__before"], counts[f"{c}__after"]) for c in casts
            if counts[f"{c}__before"] != counts[f"{c}__after"]}
print("columns where a cast dropped values (before, after):", failures or "none")

# Money values with more than 2 decimals would be silently rounded by DECIMAL(18,2). Count them.
rounded_row = df0.agg(*[
    F.sum(F.when(F.abs(F.expr(f"try_cast(`{c}` AS DOUBLE)") - F.expr(f"try_cast(`{c}` AS DECIMAL(18,2))")) > 0.005, 1)
          .otherwise(0)).alias(c)
    for c in MONEY_COLS
]).first()
rounded = rounded_row.asDict() if rounded_row is not None else {}
print("money values that would round:", {k: v for k, v in rounded.items() if v})

assert not failures, f"fix the casts or the column type for: {failures}"

# COMMAND ----------

# Step 4: apply casts, flag negative building payments (kept, not clamped), rename, dedupe.
df1 = df0.select(*[F.expr(casts[c]).alias(c) if c in casts else F.col(c) for c in ALL_COLS])
df1 = df1.withColumn(
    "isNegativeBuildingPayment",
    F.when(F.col("amountPaidOnBuildingClaim").isNotNull(), F.col("amountPaidOnBuildingClaim") < 0),
)
df1 = df1.toDF(*[snake(c) for c in df1.columns])

# id was unique in the raw profiling, so this should remove nothing. It is a guard for future loads.
silver = df1.dropDuplicates(["id"])

# COMMAND ----------

(
    silver.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER)
)

# COMMAND ----------

# Step 5: reconcile bronze to silver, and report NULL counts per column.
silver_tbl = spark.table(SILVER)
silver_rows = silver_tbl.count()
print("bronze rows:", bronze_rows, "| silver rows:", silver_rows)
assert silver_rows == bronze_rows, "silver should hold one row per bronze row"

display(silver_tbl.agg(*[F.sum(F.col(c).isNull().cast("int")).alias(c) for c in silver_tbl.columns]))
silver_tbl.printSchema()

# COMMAND ----------

# Step 6: export one Parquet file for loading into Snowflake (download it from the Volume in the UI).
spark.sql("CREATE VOLUME IF NOT EXISTS workspace.silver.exports")
(
    silver_tbl.coalesce(1)  # one file is easiest to download; the table is small
    .write.mode("overwrite").parquet(EXPORT_DIR)
)
display(dbutils.fs.ls(EXPORT_DIR))
