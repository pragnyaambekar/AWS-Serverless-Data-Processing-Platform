# Serverless Data Processing Platform

A serverless pipeline that automatically ingests and cleans datasets on AWS.

You upload a CSV file to S3. That triggers a Lambda function (Python) which cleans the data, saves the cleaned file back to S3, and stores a record of the run in DynamoDB. CloudWatch keeps logs and sends alerts if something fails. Docker and Jenkins handle packaging and deployment.

## How it works

```
CSV upload -> S3 (raw/) -> triggers Lambda -> cleans data
                                              |-> S3 (processed/)
                                              |-> DynamoDB (run details)
                                              |-> CloudWatch (logs + alarms)

Code push -> Jenkins -> run tests -> build Docker image -> deploy Lambda
```

## Tech used

- Python 3.12
- AWS Lambda (runs the code)
- Amazon S3 (stores files)
- Amazon DynamoDB (stores processing records)
- Amazon CloudWatch (logs and alerts)
- Docker (packaging)
- Jenkins (CI/CD)

## Folder structure

```
serverless-data-platform/
  README.md
  PLAN.md
  .gitignore
  requirements.txt
  src/
    handler.py            # Lambda entry point
    transform.py          # data cleaning logic
    db.py                 # DynamoDB helper
  tests/
    test_transform.py
  data/
    sample_sales_data.csv
  scripts/
    upload_to_s3.py
  infra/                  # AWS setup notes / config
  docker/
    Dockerfile
  Jenkinsfile
```

## Git flow used in this project

- `main`: stable, released code only
- `develop`: where all finished features get merged first
- `feature/*`: one branch per step, created from `develop`
- `release/*`: final checks before merging into `main`
- `hotfix/*`: quick fixes on `main`

Every feature branch is merged into `develop` with a pull request. No direct commits to `main` or `develop`.

## Commit message style

Short and clear, for example:
- `feat: add csv cleaning function`
- `fix: handle missing price values`
- `docs: update readme`
- `chore: add gitignore`

## Status

- [ ] Project setup
- [ ] S3 ingestion
- [ ] Lambda transform
- [ ] DynamoDB storage
- [ ] CloudWatch monitoring
- [ ] Docker
- [ ] Jenkins CI/CD
- [ ] Release v1.0
