"""Clean the raw DisasterDeclarationsSummaries extract into one typed Parquet file for Snowflake.

The table is small (about 70k rows), so it skips Databricks and goes straight to Snowflake staging.
Same silver rules as claims: keep needed columns, snake_case names, blanks to NULL, real types.

Usage:
    python ingestion/prepare_disasters.py
Output:
    data/silver/disaster_declarations/disaster_declarations.parquet
"""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq

RAW = Path("data/raw/DisasterDeclarationsSummaries")
OUT = Path("data/silver/disaster_declarations/disaster_declarations.parquet")

STRING_COLS = {
    "id": "id",
    "disasterNumber": "disaster_number",
    "femaDeclarationString": "fema_declaration_string",
    "state": "state",
    "fipsStateCode": "fips_state_code",
    "fipsCountyCode": "fips_county_code",  # "000" means the whole state, not one county
    "designatedArea": "designated_area",
    "declarationType": "declaration_type",  # DR major disaster, EM emergency, FM fire management
    "declarationTitle": "declaration_title",
    "incidentType": "incident_type",
}
DATE_COLS = {
    "declarationDate": "declaration_date",
    "incidentBeginDate": "incident_begin_date",
    "incidentEndDate": "incident_end_date",
}
INT_COLS = {"fyDeclared": "fy_declared"}


def blank_to_null(arr: pa.ChunkedArray) -> pa.ChunkedArray:
    arr = pc.utf8_trim_whitespace(arr)
    return pc.if_else(pc.equal(arr, ""), pa.scalar(None, pa.string()), arr)


def main() -> None:
    dataset = ds.dataset(RAW, format="parquet", partitioning="hive", exclude_invalid_files=True)
    raw = dataset.to_table()

    cols = {}
    for src, dst in STRING_COLS.items():
        cols[dst] = blank_to_null(raw.column(src))
    for src, dst in DATE_COLS.items():
        # Values look like 2005-08-29T00:00:00.000Z; the first 10 characters are the date.
        cols[dst] = pc.cast(pc.utf8_slice_codeunits(blank_to_null(raw.column(src)), 0, 10), pa.date32())
    for src, dst in INT_COLS.items():
        cols[dst] = pc.cast(raw.column(src), pa.int32())

    table = pa.table(cols)

    # Same checks as claims silver: no rows lost, no value lost in a cast, id unique.
    assert table.num_rows == raw.num_rows
    for src, dst in DATE_COLS.items():
        before = pc.count(blank_to_null(raw.column(src))).as_py()
        assert before == pc.count(table.column(dst)).as_py(), f"{dst}: values lost in the date cast"
    assert pc.count_distinct(table.column("id")).as_py() == table.num_rows, "id is not unique"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUT)
    print(f"{table.num_rows:,} rows, {table.num_columns} columns -> {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
