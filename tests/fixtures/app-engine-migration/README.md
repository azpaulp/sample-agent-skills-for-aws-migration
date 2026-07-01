# Fixture: app-engine-migration

Validates that Google App Engine resources correctly map to AWS Elastic Beanstalk.

## What it tests

- App Engine Standard (Python 3.9) → Elastic Beanstalk with Python platform
- PaaS-to-PaaS mapping preserves managed platform model
- Supporting resources (Cloud Storage, Service Account) still map correctly
- Cloud Run (in other fixtures) does NOT default to EB without explicit preference

## Resources

| Resource | Type | Expected AWS Target |
|----------|------|-------------------|
| `google_app_engine_application` | Primary | Elastic Beanstalk |
| `google_app_engine_standard_app_version` | Primary | (part of EB config) |
| `google_storage_bucket` | Secondary | S3 |
| `google_service_account` | Secondary | IAM Role |
