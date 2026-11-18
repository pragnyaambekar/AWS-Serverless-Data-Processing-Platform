import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

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


def test_handler_skips_files_outside_raw(monkeypatch):
    fake = FakeS3({})
    monkeypatch.setattr(handler, "get_s3", lambda: fake)

    handler.lambda_handler(make_event("processed/sample_sales_data.csv"), None)

    assert fake.saved == {}