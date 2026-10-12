"""Pull an OpenFEMA dataset page by page and land it as partitioned Parquet.

Usage:
    python ingestion/extract_openfema.py FimaNfipClaims
    python ingestion/extract_openfema.py FimaNfipClaims --max-pages 2   # smoke test
    python ingestion/extract_openfema.py FimaNfipClaims --restart       # ignore checkpoint

Output layout (Hive style, which Spark and Snowflake both understand):
    data/raw/<dataset>/yearOfLoss=2005/page-000010000-0.parquet
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests

BASE_URL = "https://www.fema.gov/api/open/v2"
PAGE_SIZE = 10_000  # OpenFEMA caps $top at 10,000 rows per request
DEFAULT_PARTITION_COL = "yearOfLoss"
UNKNOWN_PARTITION = "unknown"

log = logging.getLogger("openfema")


def fetch_page(session: requests.Session, dataset: str, skip: int, *, top: int = PAGE_SIZE,
               odata_filter: str | None = None, with_count: bool = False,
               retries: int = 5, base_url: str = BASE_URL) -> dict:
    """Fetch one page. Retries transient failures with exponential backoff (2s, 4s, 8s ...)."""
    params = {"$top": top, "$skip": skip, "$orderby": "id"}  # stable order, or paging can skip/duplicate rows
    if odata_filter:
        params["$filter"] = odata_filter
    if with_count:
        params["$count"] = "true"
    url = f"{base_url}/{dataset}"

    for attempt in range(retries + 1):
        try:
            resp = session.get(url, params=params, timeout=120)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            resp.raise_for_status()
            return resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError, ValueError) as exc:
            if attempt == retries:
                raise
            wait = 2 ** (attempt + 1)
            log.warning("skip=%s attempt %s failed (%s), retrying in %ss", skip, attempt + 1, exc, wait)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def _to_str(value):
    """Bronze principle: land values as strings, type them later in silver.

    A page where a column is all null would otherwise infer a different Parquet type than
    the next page, which breaks reading the dataset back as one table.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def to_table(rows: list[dict], partition_col: str, ingested_at: str) -> pa.Table:
    # Union of keys: OpenFEMA omits null fields on some records.
    columns = sorted({key for row in rows for key in row})
    data = {col: [_to_str(row.get(col)) for row in rows] for col in columns}
    if partition_col not in data:
        data[partition_col] = [None] * len(rows)
    # Null partition values would become __HIVE_DEFAULT_PARTITION__, so name them explicitly.
    data[partition_col] = [v if v else UNKNOWN_PARTITION for v in data[partition_col]]
    data["_ingested_at"] = [ingested_at] * len(rows)  # lineage column
    return pa.table({k: pa.array(v, type=pa.string()) for k, v in data.items()})


def write_page(table: pa.Table, out_dir: Path, skip: int, partition_col: str) -> None:
    # File name is derived from the page offset, so re-running a page overwrites its own
    # files instead of duplicating rows. That is what makes the job idempotent.
    pq.write_to_dataset(
        table,
        root_path=str(out_dir),
        partition_cols=[partition_col],
        basename_template=f"page-{skip:09d}-{{i}}.parquet",
        existing_data_behavior="overwrite_or_ignore",
        compression="snappy",
    )


def load_checkpoint(path: Path) -> int:
    if path.exists():
        return json.loads(path.read_text())["next_skip"]
    return 0


def save_checkpoint(path: Path, next_skip: int, total: int | None) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"next_skip": next_skip, "total": total,
                               "updated_at": datetime.now(timezone.utc).isoformat()}))
    tmp.replace(path)  # atomic, so a crash never leaves a half-written checkpoint


def extract(dataset: str, out_root: Path, *, partition_col: str = DEFAULT_PARTITION_COL,
            odata_filter: str | None = None, max_pages: int | None = None,
            restart: bool = False, pause: float = 0.2, page_size: int = PAGE_SIZE, base_url: str = BASE_URL,
            session: requests.Session | None = None) -> int:
    """Returns the number of rows written in this run."""
    out_dir = out_root / dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = out_dir / "_checkpoint.json"
    if restart and checkpoint.exists():
        checkpoint.unlink()

    session = session or requests.Session()
    skip = load_checkpoint(checkpoint)
    if skip:
        log.info("resuming from skip=%s", skip)

    total = None
    rows_written = pages = 0
    while max_pages is None or pages < max_pages:
        payload = fetch_page(session, dataset, skip, top=page_size, odata_filter=odata_filter,
                             with_count=(total is None), base_url=base_url)
        if total is None:
            total = payload.get("metadata", {}).get("count")
            log.info("server reports %s matching rows", total)
        rows = payload.get(dataset, [])
        if not rows:
            break

        ingested_at = datetime.now(timezone.utc).isoformat()
        write_page(to_table(rows, partition_col, ingested_at), out_dir, skip, partition_col)

        skip += len(rows)
        pages += 1
        rows_written += len(rows)
        save_checkpoint(checkpoint, skip, total)  # only after the write succeeded
        log.info("skip=%s / %s", skip, total)

        if len(rows) < page_size:
            break
        time.sleep(pause)  # be polite to a free public API

    log.info("done: %s rows this run", rows_written)
    return rows_written


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("dataset", help="OpenFEMA dataset, e.g. FimaNfipClaims")
    p.add_argument("--out", type=Path, default=Path("data/raw"), help="output root (gitignored)")
    p.add_argument("--partition-col", default=DEFAULT_PARTITION_COL)
    p.add_argument("--filter", dest="odata_filter", help="raw OData $filter, e.g. \"yearOfLoss ge 2020\"")
    p.add_argument("--max-pages", type=int, help="stop after N pages (smoke tests)")
    p.add_argument("--restart", action="store_true", help="ignore the checkpoint and start from page 1")
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    extract(args.dataset, args.out, partition_col=args.partition_col, odata_filter=args.odata_filter,
            max_pages=args.max_pages, restart=args.restart)
    return 0


if __name__ == "__main__":
    sys.exit(main())
