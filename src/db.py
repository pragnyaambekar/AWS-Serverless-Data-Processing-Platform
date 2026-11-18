"""Save a record of every processing run to DynamoDB."""

import os
from datetime import datetime, timezone

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "sales-processing-runs")

_table = None


def get_table():
    """Connect to the DynamoDB table once and reuse it."""
    global _table
    if _table is None:
        _table = boto3.resource("dynamodb").Table(TABLE_NAME)
    return _table


def record_run(file_key, status, stats=None, output_key=None, error=None):
    """Save one item describing a run. Returns the item that was saved.

    file_key     -> partition key (which file)
    processed_at -> sort key (when this run happened)
    """
    item = {
        "file_key": file_key,
        "processed_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "status": status,
    }
    if stats:
        item.update(stats)
    if output_key:
        item["output_key"] = output_key
    if error is not None:
        item["error"] = str(error)[:500]  # keep the record small

    get_table().put_item(Item=item)
    return item