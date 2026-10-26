import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from transform import clean_csv, clean_row, normalize_date, rows_to_csv  # noqa: E402

SAMPLE_FILE = ROOT / "data" / "sample_sales_data.csv"


def test_normalize_date_handles_both_formats():
    assert normalize_date("2026-01-05") == "2026-01-05"
    assert normalize_date("01/11/2026") == "2026-01-11"


def test_normalize_date_returns_none_for_garbage():
    assert normalize_date("not a date") is None


def test_clean_row_trims_spaces_and_fixes_region():
    row = {
        "order_id": "1005", "customer_name": "  Rahul Verma ", "product": "Laptop",
        "quantity": "1", "price": "899.99", "order_date": "2026-01-08", "region": "WEST",
    }
    cleaned, reason = clean_row(row)
    assert reason is None
    assert cleaned["customer_name"] == "Rahul Verma"
    assert cleaned["region"] == "West"


def test_clean_row_adds_total():
    row = {
        "order_id": "1014", "customer_name": "Chris Lee", "product": "Keyboard",
        "quantity": "4", "price": "49.5", "order_date": "2026-01-15", "region": "West",
    }
    cleaned, _ = clean_row(row)
    assert cleaned["total"] == 198.0


def test_clean_row_rejects_negative_quantity():
    row = {
        "order_id": "1012", "customer_name": "Sam Wilson", "product": "Mouse",
        "quantity": "-1", "price": "19.99", "order_date": "2026-01-13", "region": "East",
    }
    cleaned, reason = clean_row(row)
    assert cleaned is None
    assert reason is not None


def test_clean_row_rejects_missing_price():
    row = {
        "order_id": "1008", "customer_name": "Anita Desai", "product": "Monitor",
        "quantity": "1", "price": "", "order_date": "2026-01-10", "region": "North",
    }
    cleaned, reason = clean_row(row)
    assert cleaned is None
    assert "price" in reason


def test_clean_csv_on_sample_file():
    result = clean_csv(SAMPLE_FILE.read_text())
    assert result["stats"] == {
        "total_rows": 16,
        "cleaned_rows": 11,
        "duplicates_removed": 1,
        "invalid_rows_removed": 4,
    }


def test_rows_to_csv_has_total_column():
    result = clean_csv(SAMPLE_FILE.read_text())
    text = rows_to_csv(result["rows"])
    assert text.splitlines()[0].endswith("total")
    assert len(text.splitlines()) == 12  # header + 11 rows