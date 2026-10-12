import sys
from pathlib import Path

import pyarrow.dataset as ds

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingestion"))
import extract_openfema as ex  # noqa: E402

DATASET = "FimaNfipClaims"


class FakeSession:
    """Serves a fixed list of rows the way OpenFEMA pages them ($top/$skip)."""

    def __init__(self, rows):
        self.rows, self.calls = rows, []

    def get(self, url, params, timeout):
        self.calls.append(dict(params))
        top, skip = params["$top"], params["$skip"]
        body = {DATASET: self.rows[skip:skip + top]}
        if params.get("$count"):
            body["metadata"] = {"count": len(self.rows)}
        return FakeResponse(body)


class FakeResponse:
    status_code = 200

    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def make_rows(n):
    rows = [{"id": f"{i:05d}", "yearOfLoss": 2000 + i % 3, "amountPaid": i * 1.5} for i in range(n)]
    rows[0].pop("yearOfLoss")  # OpenFEMA drops null fields, so one row has no partition value
    return rows


def test_pages_all_rows_and_partitions(tmp_path):
    rows = make_rows(10)
    session = FakeSession(rows)
    assert ex.extract(DATASET, tmp_path, session=session, pause=0, page_size=4) == 10

    table = ds.dataset(tmp_path / DATASET, partitioning="hive").to_table()
    assert table.num_rows == 10
    assert len({*table["id"].to_pylist()}) == 10
    assert {"2000", "2001", "2002", "unknown"} == set(map(str, table["yearOfLoss"].to_pylist()))
    assert "_ingested_at" in table.column_names
    assert all(c["$orderby"] == "id" for c in session.calls)


def test_rerun_is_idempotent_and_resumes(tmp_path):
    rows = make_rows(10)

    assert ex.extract(DATASET, tmp_path, session=FakeSession(rows), pause=0, page_size=4, max_pages=1) == 4
    assert ex.load_checkpoint(tmp_path / DATASET / "_checkpoint.json") == 4

    assert ex.extract(DATASET, tmp_path, session=FakeSession(rows), pause=0, page_size=4) == 6  # resumed
    assert ex.extract(DATASET, tmp_path, session=FakeSession(rows), pause=0, page_size=4, restart=True) == 10

    # a full restart overwrites the same page files, so there are no duplicates
    assert ds.dataset(tmp_path / DATASET, partitioning="hive").count_rows() == 10
