# Phase 3 performance notes: small files vs compacted

Environment: Databricks Free Edition, serverless compute, `workspace.bronze.raw_files` Volume.
Dataset: FimaNfipClaims, 2,721,780 rows, raw Parquet as extracted (~13k small files, Hive-partitioned by yearOfLoss, all columns strings).

## Baseline (before compaction)

| Measure | Result | Notes |
|---------|--------|-------|
| Unzip ~13.4k files into the Volume | 1,354 s (~22.5 min) | Python `zipfile.extractall`, one small write per file |
| `spark.read.parquet(path).count()` | 7.9 s, 7.1 s | Two runs; the second came from the combined timing cell |
| `groupBy("yearOfLoss").count().collect()` | 6.4 s | One run |

## Caveats to resolve before comparing

- Only two `count()` runs and one group-by run so far. Repeat to 3 runs each and record every one; a cold first run is usually slower.
- `count()` on Parquet can be answered mostly from file footers, so it mostly measures listing and opening ~13k files. Add a query that reads a column too.
- Record the same measures after compaction (target: a few large files per yearOfLoss, or Delta `OPTIMIZE`) and report the ratio.

## Bronze Delta table (first write, unpartitioned)

`workspace.bronze.fima_nfip_claims`, written by `spark/01_bronze_claims.py`.

| Measure | Raw Parquet in Volume | Bronze Delta |
|---------|----------------------|--------------|
| Files | ~13.4k | 9 |
| Size | 689 MB (local), 390 MB zipped | 180,045,227 bytes (~180 MB) |
| `count()` | 7.9 s, 7.1 s | 1.4 s, 0.7 s, 0.5 s |
| group by year | 6.4 s | 2.4 s, 0.9 s, 0.8 s |

Reading the bronze runs: the first run is the slowest (1.4 s, 2.4 s) and later runs speed up, which looks like warm-up or caching. First-run comparison is about 5x for count (7.9 s vs 1.4 s) and about 2.7x for group by (6.4 s vs 2.4 s). Raw runs were not repeated enough to compare warm runs fairly; rerun the raw path 3 times to get a matching warm set. The comparison also mixes two changes (Delta format and file layout), so it does not show which one helped.

Size note: the smaller size is likely because Spark wrote a few large files, so Parquet compresses repeated string values far better than many tiny files do. This is unverified; compare compression settings before claiming it.

## After further experiments (partitioning, OPTIMIZE, Z-ORDER)

_To fill in during Phase 3._
