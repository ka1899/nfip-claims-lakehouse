# Phase 3 performance notes: small files vs compacted

Environment: Databricks Free Edition, serverless compute, `workspace.bronze.raw_files` Volume.
Dataset: FimaNfipClaims, 2,721,780 rows, raw Parquet as extracted (~13k small files, Hive-partitioned by yearOfLoss, all columns strings).

## Baseline (before compaction)

| Measure | Result | Notes |
|---------|--------|-------|
| Unzip ~13.4k files into the Volume | 1,354 s (~22.5 min) | Python `zipfile.extractall`, one small write per file |
| `spark.read.parquet(path).count()` | 7.9 s | Single run. Cache state unknown (see below) |

## Caveats to resolve before comparing

- One run is not a benchmark. Repeat 3 times and record each run; the first run on a cold cluster is usually slower.
- `count()` on Parquet can be answered mostly from file footers, so it mostly measures listing and opening ~13k files. Add a query that reads a column too.
- Record the same measures after compaction (target: a few large files per yearOfLoss, or Delta `OPTIMIZE`) and report the ratio.

## After compaction

_To fill in during Phase 3._
