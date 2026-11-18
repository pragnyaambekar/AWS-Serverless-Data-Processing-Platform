import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import db  # noqa: E402


class FakeTable:
    def __init__(self):
        self.items = []

    def put_item(self, Item):
        self.items.append(Item)


def test_record_run_saves_expected_fields(monkeypatch):
    table = FakeTable()
    monkeypatch.setattr(db, "get_table", lambda: table)

    item = db.record_run(
        "raw/a.csv",
        "SUCCESS",
        stats={"total_rows": 5, "cleaned_rows": 4},
        output_key="processed/a.csv",
    )

    assert table.items == [item]
    assert item["file_key"] == "raw/a.csv"
    assert item["status"] == "SUCCESS"
    assert item["total_rows"] == 5
    assert item["output_key"] == "processed/a.csv"
    assert "error" not in item


def test_record_run_shortens_long_errors(monkeypatch):
    table = FakeTable()
    monkeypatch.setattr(db, "get_table", lambda: table)

    item = db.record_run("raw/a.csv", "FAILED", error="x" * 1000)

    assert len(item["error"]) == 500


def test_processed_at_ends_with_utc_offset(monkeypatch):
    table = FakeTable()
    monkeypatch.setattr(db, "get_table", lambda: table)

    item = db.record_run("raw/a.csv", "SUCCESS")

    assert item["processed_at"].endswith("+00:00")