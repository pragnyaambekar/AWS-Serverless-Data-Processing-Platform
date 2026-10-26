"""Cleaning logic for the sales CSV files.

This file only uses Python's standard library, so it needs no extra
packages when we deploy it to AWS Lambda later.
"""

import csv
import io
from datetime import datetime

REQUIRED_FIELDS = ["order_id", "customer_name", "product", "quantity", "price", "order_date", "region"]
OUTPUT_FIELDS = REQUIRED_FIELDS + ["total"]
DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y"]


def normalize_date(value):
    """Turn a date string into YYYY-MM-DD. Return None if we can't read it."""
    value = (value or "").strip()
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(value, date_format).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def clean_row(row):
    """Clean one row.

    Returns (clean_row, None) if the row is good,
    or (None, reason) if the row should be thrown away.
    """
    # 1. Strip spaces from every value
    row = {key: (value or "").strip() for key, value in row.items() if key}

    # 2. Required fields must not be empty
    for field in REQUIRED_FIELDS:
        if not row.get(field):
            return None, f"missing {field}"

    # 3. Numbers must really be numbers
    try:
        quantity = int(row["quantity"])
        price = float(row["price"])
    except ValueError:
        return None, "quantity or price is not a number"

    if quantity <= 0 or price < 0:
        return None, "quantity must be above 0 and price cannot be negative"

    # 4. Dates must be readable
    order_date = normalize_date(row["order_date"])
    if order_date is None:
        return None, "bad date format"

    # 5. Build the cleaned row
    cleaned = {
        "order_id": row["order_id"],
        "customer_name": row["customer_name"],
        "product": row["product"],
        "quantity": quantity,
        "price": round(price, 2),
        "order_date": order_date,
        "region": row["region"].title(),
        "total": round(quantity * price, 2),
    }
    return cleaned, None


def clean_csv(csv_text):
    """Clean a whole CSV (given as text).

    Returns a dict with the cleaned rows, summary numbers, and the
    reasons rows were rejected.
    """
    reader = csv.DictReader(io.StringIO(csv_text))

    cleaned_rows = []
    rejected = []
    seen = set()
    duplicates_removed = 0
    total_rows = 0

    for row in reader:
        total_rows += 1
        cleaned, reason = clean_row(row)

        if reason:
            rejected.append({"order_id": (row.get("order_id") or "").strip(), "reason": reason})
            continue

        key = tuple(cleaned.values())
        if key in seen:
            duplicates_removed += 1
            continue
        seen.add(key)
        cleaned_rows.append(cleaned)

    return {
        "rows": cleaned_rows,
        "stats": {
            "total_rows": total_rows,
            "cleaned_rows": len(cleaned_rows),
            "duplicates_removed": duplicates_removed,
            "invalid_rows_removed": len(rejected),
        },
        "rejected": rejected,
    }


def rows_to_csv(rows):
    """Turn cleaned rows back into CSV text."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()