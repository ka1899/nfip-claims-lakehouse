# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze: FimaNfipClaims
# MAGIC Raw Parquet in the Volume -> Delta table `workspace.bronze.fima_nfip_claims`.
# MAGIC Bronze stays faithful to the source: no cleaning, every column a string. Typing and dedup happen in silver.

# COMMAND ----------

from pyspark.sql import functions as F

SOURCE_PATH = "/Volumes/workspace/bronze/raw_files/FimaNfipClaims"
TARGET_TABLE = "workspace.bronze.fima_nfip_claims"
EXPECTED_ROWS = 2_721_780  # the API's $count at extraction time

# COMMAND ----------

# Spark rebuilds yearOfLoss from the folder names and guesses an integer type.
# Bronze keeps everything as strings, so cast it back.
df = (
    spark.read.parquet(SOURCE_PATH)
    .withColumn("yearOfLoss", F.col("yearOfLoss").cast("string"))
)

non_string = [(f.name, f.dataType.simpleString()) for f in df.schema.fields if f.dataType.simpleString() != "string"]
assert not non_string, f"bronze should be all strings, found: {non_string}"

# COMMAND ----------

# Unpartitioned on purpose: ~2.7M rows is small for a partitioned table.
# Partitioning by yearOfLoss is a separate Phase 3 experiment with its own timings.
(
    df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")  # lets us rerun this notebook safely
    .saveAsTable(TARGET_TABLE)
)

# COMMAND ----------

# Reconcile: the table must hold exactly what the source held.
rows = spark.table(TARGET_TABLE).count()
print("rows in bronze:", rows)
assert rows == EXPECTED_ROWS, f"expected {EXPECTED_ROWS}, got {rows}"

# COMMAND ----------

# How many files did Delta write? Compare with the ~13k raw files for the Phase 3 notes.
display(spark.sql(f"DESCRIBE DETAIL {TARGET_TABLE}").select("numFiles", "sizeInBytes"))
