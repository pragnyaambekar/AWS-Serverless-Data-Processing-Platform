"""AWS Lambda entry point.

Flow: a CSV lands in s3://<bucket>/raw/  ->  S3 triggers this function  ->
we read the file, clean it with transform.py, save the result to
s3://<bucket>/processed/, and record the run in DynamoDB.
"""

import json
import logging
from urllib.parse import unquote_plus

import boto3

import db
from transform import clean_csv, rows_to_csv

RAW_PREFIX = "raw/"
PROCESSED_PREFIX = "processed/"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_s3_client = None


def get_s3():
    """Create the S3 client once and reuse it (faster on repeat runs)."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
    return _s3_client


def record_failure(key, error):
    """Try to save a FAILED record. Never hide the original error if this fails too."""
    try:
        db.record_run(key, "FAILED", error=error)
    except Exception:
        logger.exception("Could not save failure record for %s", key)


def process_record(record):
    """Handle one S3 upload event record."""
    bucket = record["s3"]["bucket"]["name"]
    # S3 sends keys URL-encoded (spaces become '+'), so we decode them first
    key = unquote_plus(record["s3"]["object"]["key"])

    # Safety check: only handle files in raw/. Never touch processed/.
    if not key.startswith(RAW_PREFIX):
        logger.info("Skipping %s (not in %s)", key, RAW_PREFIX)
        return {"key": key, "status": "skipped"}

    try:
        logger.info("Processing s3://%s/%s", bucket, key)
        s3 = get_s3()

        # utf-8-sig also handles CSVs saved from Excel (they start with a hidden BOM mark)
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8-sig")

        result = clean_csv(body)

        output_key = PROCESSED_PREFIX + key[len(RAW_PREFIX):]
        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=rows_to_csv(result["rows"]).encode("utf-8"),
            ContentType="text/csv",
        )

        logger.info("Done %s -> %s stats=%s", key, output_key, json.dumps(result["stats"]))
        if result["rejected"]:
            logger.info("Rejected rows: %s", json.dumps(result["rejected"]))

        db.record_run(key, "SUCCESS", stats=result["stats"], output_key=output_key)
    except Exception as error:
        record_failure(key, error)
        raise

    return {"key": key, "output_key": output_key, "status": "processed", "stats": result["stats"]}


def lambda_handler(event, context):
    """Lambda calls this function. 'event' holds details of what triggered it."""
    results = []
    for record in event.get("Records", []):
        try:
            results.append(process_record(record))
        except Exception:
            # Log the full error, then re-raise so Lambda marks this run as failed.
            # (Step 5: a CloudWatch alarm will watch for these failures.)
            logger.exception("Failed to process record: %s", json.dumps(record))
            raise
    return {"statusCode": 200, "body": json.dumps(results)}