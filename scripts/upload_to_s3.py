"""Upload a local file to the raw/ folder of our S3 bucket.

Usage:
    export BUCKET_NAME=your-bucket-name
    python scripts/upload_to_s3.py data/sample_sales_data.csv
"""

import os
import sys

import boto3
from botocore.exceptions import ClientError

RAW_PREFIX = "raw/"


def upload_file(local_path, bucket, key):
    """Upload one file to S3."""
    s3 = boto3.client("s3")
    s3.upload_file(local_path, bucket, key)
    print(f"Uploaded {local_path} -> s3://{bucket}/{key}")


def list_files(bucket, prefix):
    """Print everything stored under a prefix (like a folder)."""
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    items = response.get("Contents", [])
    if not items:
        print(f"Nothing found under {prefix}")
        return
    print(f"Files under {prefix}:")
    for item in items:
        print(f"  {item['Key']}  ({item['Size']} bytes)")


def main():
    bucket = os.environ.get("BUCKET_NAME")
    if not bucket:
        print("Set BUCKET_NAME first, e.g. export BUCKET_NAME=my-bucket")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python scripts/upload_to_s3.py <path-to-file>")
        sys.exit(1)

    local_path = sys.argv[1]
    if not os.path.isfile(local_path):
        print(f"File not found: {local_path}")
        sys.exit(1)

    key = RAW_PREFIX + os.path.basename(local_path)

    try:
        upload_file(local_path, bucket, key)
        list_files(bucket, RAW_PREFIX)
    except ClientError as error:
        print(f"AWS error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
