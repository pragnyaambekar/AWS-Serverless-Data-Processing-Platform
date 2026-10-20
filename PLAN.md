# Project Plan: What We Build and What You Learn

Rough time: 2 to 3 weeks if you do 1 or 2 steps per day. No rush, go at your own speed.

For every step we will do the same 4 things:
1. Understand the concept in simple words
2. Do it by hand first (AWS console), so you see what is happening
3. Do it with code
4. Commit, open a PR, merge (git flow practice)

---

## Phase 0: Prep (before step 1)

**What we do**
- Check your tools (Git, Python, Docker, AWS CLI)
- Create an AWS account
- Set a billing alert so you never get a surprise bill
- Create an IAM user (never use the root account for daily work)

**What you learn**
- What AWS is, regions, free tier
- What IAM is (users, permissions, access keys)
- Why we protect keys (never push them to GitHub)

**Interview line:** "I used a least-privilege IAM user and set billing alarms to control cost."

---

## Step 1: `feature/project-setup`

**What we do**
- Create the GitHub repo with `main` and `develop`
- Add folder structure, README, .gitignore, sample data
- Make a Python virtual environment

**What you learn**
- Git flow in practice (branches, PRs, merging)
- Clean project structure
- Virtual environments

---

## Step 2: `feature/s3-ingestion`

**What we do**
- Create an S3 bucket with `raw/` and `processed/` folders
- Upload the sample CSV by clicking in the console
- Then upload with Python (boto3)

**What you learn**
- What S3 is (buckets, objects, keys)
- boto3 (the Python library for AWS)
- Configuring the AWS CLI

**Interview line:** "Files land in S3, and S3 events trigger the processing."

---

## Step 3: `feature/lambda-transform`

**What we do**
- Write the cleaning logic (remove duplicates, fix missing values, standardize columns)
- Write unit tests with pytest
- Create the Lambda function and connect it to the S3 upload event

**What you learn**
- What Lambda is and what "serverless" really means
- Event-driven design (S3 event -> Lambda)
- Lambda execution roles and permissions
- Writing testable code

---

## Step 4: `feature/dynamodb-storage`

**What we do**
- Create a DynamoDB table
- Save a record for every processed file (file name, row counts, status, timestamp)

**What you learn**
- NoSQL basics, partition keys (you know MongoDB, so this will feel familiar)
- Reading and writing items with boto3
- Why we store metadata

---

## Step 5: `feature/cloudwatch-monitoring`

**What we do**
- Add structured logging in Lambda
- Look at logs in CloudWatch
- Create an alarm that emails you when Lambda fails

**What you learn**
- Logs, metrics, alarms
- How to debug a serverless app
- Why monitoring matters in production

---

## Step 6: `feature/docker`

**What we do**
- Write a Dockerfile for the Lambda code
- Build the image and test it locally

**What you learn**
- Images vs containers
- Packaging Lambda as a container image
- Amazon ECR basics

---

## Step 7: `feature/jenkins-cicd`

**What we do**
- Run Jenkins locally in Docker
- Write a Jenkinsfile: test -> build -> deploy
- Trigger the pipeline on a push

**What you learn**
- What CI/CD is and why teams use it
- Pipeline stages
- Safe handling of credentials in Jenkins

---

## Step 8: `release/v1.0`

**What we do**
- Final cleanup and testing
- Merge `release/v1.0` into `main` and `develop`
- Tag `v1.0`
- Practice one `hotfix/` branch
- Delete AWS resources so you don't get charged

**What you learn**
- Full git flow release cycle
- Cleanup and cost control

---

## At the end you will be able to say

- I built an event-driven serverless pipeline on AWS
- I set up monitoring and alerts with CloudWatch
- I automated builds and deployments with Docker and Jenkins
- I followed git flow with feature, release, and hotfix branches
