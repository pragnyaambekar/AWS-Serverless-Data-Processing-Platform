import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import db  # noqa: E402
import handler  # noqa: E402

SAMPLE_FILE = ROOT / "data" / "sample_sales_data.csv"


class FakeS3:
    """A pretend S3 so we can test without touching AWS."""

    def __init__(self, files):
        self.files = files  # {key: bytes}
        self.saved = {}  # what the handler wrote

    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.files[Key])}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.saved[Key] = Body


class FakeTable:
    """A pretend DynamoDB table."""

    def __init__(self):
        self.items = []

    def put_item(self, Item):
        self.items.append(Item)


@pytest.fixture(autouse=True)
def fake_table(monkeypatch):
    """Every test in this file uses a fake table, so nothing ever hits real AWS."""
    table = FakeTable()
    monkeypatch.setattr(db, "get_table", lambda: table)
    return table


def make_event(key):
    return {"Records": [{"s3": {"bucket": {"name": "test-bucket"}, "object": {"key": key}}}]}


def test_handler_cleans_file_and_writes_to_processed(monkeypatch):
    fake = FakeS3({"raw/sample_sales_data.csv": SAMPLE_FILE.read_bytes()})
    monkeypatch.setattr(handler, "get_s3", lambda: fake)

    response = handler.lambda_handler(make_event("raw/sample_sales_data.csv"), None)

    assert response["statusCode"] == 200
    assert "processed/sample_sales_data.csv" in fake.saved
    lines = fake.saved["processed/sample_sales_data.csv"].decode().splitlines()
    assert len(lines) == 12  # header + 11 cleaned rows


def test_handler_decodes_url_encoded_keys(monkeypatch):
    fake = FakeS3({"raw/my file.csv": SAMPLE_FILE.read_bytes()})
    monkeypatch.setattr(handler, "get_s3", lambda: fake)

    handler.lambda_handler(make_event("raw/my+file.csv"), None)

    assert "processed/my file.csv" in fake.saved


def test_handler_skips_files_outside_raw(monkeypatch, fake_table):
    fake = FakeS3({})
    monkeypatch.setattr(handler, "get_s3", lambda: fake)

    handler.lambda_handler(make_event("processed/sample_sales_data.csv"), None)

    assert fake.saved == {}
    assert fake_table.items == []  # skipped files are not recorded


def test_success_run_is_recorded(monkeypatch, fake_table):
    fake = FakeS3({"raw/sample_sales_data.csv": SAMPLE_FILE.read_bytes()})
    monkeypatch.setattr(handler, "get_s3", lambda: fake)

    handler.lambda_handler(make_event("raw/sample_sales_data.csv"), None)

    assert len(fake_table.items) == 1
    item = fake_table.items[0]
    assert item["file_key"] == "raw/sample_sales_data.csv"
    assert item["status"] == "SUCCESS"
    assert item["output_key"] == "processed/sample_sales_data.csv"
    assert item["total_rows"] == 16
    assert item["cleaned_rows"] == 11
    assert item["duplicates_removed"] == 1
    assert item["invalid_rows_removed"] == 4
    assert "processed_at" in item


def test_failed_run_is_recorded_and_still_raises(monkeypatch, fake_table):
    fake = FakeS3({})  # file is missing, so get_object will fail
    monkeypatch.setattr(handler, "get_s3", lambda: fake)

    with pytest.raises(KeyError):
        handler.lambda_handler(make_event("raw/missing.csv"), None)

    assert len(fake_table.items) == 1
    item = fake_table.items[0]
    assert item["file_key"] == "raw/missing.csv"
    assert item["status"] == "FAILED"
    assert "error" in item


def test_original_error_is_not_hidden_if_saving_failure_also_fails(monkeypatch):
    fake = FakeS3({})
    monkeypatch.setattr(handler, "get_s3", lambda: fake)

    def broken_record_run(*args, **kwargs):
        raise RuntimeError("DynamoDB is down")

    monkeypatch.setattr(db, "record_run", broken_record_run)

    # We should still see the ORIGINAL problem (KeyError), not the DynamoDB one
    with pytest.raises(KeyError):
        handler.lambda_handler(make_event("raw/missing.csv"), None)