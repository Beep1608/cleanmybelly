# Infrastructure Architecture Planning

This document outlines the directory structure, environment segregation, and architectural best practices for the main infrastructure (`/infra`) of the **cleanmybelly** project.

---

## 1. Directory Structure

To separate environments and isolate components, we use a folder-segmented structure. This approach minimizes the blast radius and decouples the lifecycle of the frontend and backend.

```
aws/infra/
├── modules/
│   ├── backend/
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── dynamodb.tf
│   │   ├── lambda.tf
│   │   ├── api_gateway.tf
│   │   └── cloudwatch.tf
│   └── frontend/
│       ├── variables.tf
│       ├── outputs.tf
│       ├── s3.tf
│       ├── cloudfront.tf
│       ├── route53.tf
│       └── acm.tf
├── shared/
│   └── networking/
│       ├── dns-zone/
│       │   ├── main.tf
│       │   ├── providers.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── certificates/
│           ├── main.tf
│           ├── providers.tf
│           ├── variables.tf
│           └── outputs.tf
└── environments/
    ├── dev/
    │   ├── backend/
    │   │   ├── providers.tf
    │   │   ├── main.tf
    │   │   ├── variables.tf
    │   │   └── outputs.tf
    │   └── frontend/
    │       ├── providers.tf
    │       ├── main.tf
    │       ├── variables.tf
    │       └── outputs.tf
    └── prod/
        ├── backend/
        │   ├── providers.tf
        │   ├── main.tf
        │   ├── variables.tf
        │   └── outputs.tf
        └── frontend/
            ├── providers.tf
            ├── main.tf
            ├── variables.tf
            └── outputs.tf
```

---

## 2. Segmentation Strategy

### Dev vs. Prod Environments
*   **Complete Isolation**: The development (`dev`) and production (`prod`) environments are completely separated. They have different state keys in S3 and utilize different naming prefixes (e.g., `cleanmybelly-dev-*` vs. `cleanmybelly-prod-*`).
*   **Variable Customization**: Differences between environments (e.g., custom domains, database capacity, deployment regions) are managed via variables in each environment's root `variables.tf` file.

### Frontend vs. Backend Components
*   **Decoupled Lifecycle**: The backend (Lambda, API Gateway, DynamoDB) and frontend (S3 static files, CloudFront) are managed in separate Terraform states. This allows frontend visual updates to deploy without risking backend compute and database alterations.
*   **Resource Cross-Reference**: The frontend code can dynamically pull outputs from the backend (such as the API Gateway endpoint URL) using the `terraform_remote_state` data source.

---

## 3. Core Architectural Best Practices

### A. Reusable Modules
*   Define all resource declarations (S3, CloudFront, Lambda, API Gateway) within the `infra/modules/` directory.
*   The environment directories (`dev/` and `prod/`) should only contain module instantiation blocks referencing the local source (e.g., `source = "../../modules/backend"`).
*   This keeps configuration DRY (Don't Repeat Yourself) and guarantees that development and production are structurally identical.

### B. Remote State Configuration
*   Each environment and component must define its own unique state key in the S3 backend block.
*   All states will use the native S3 locking option (`use_lockfile = true`).

Example S3 backend keys:
*   DNS Zone: `cleanmybelly/infra/shared/networking/dns-zone/terraform.tfstate`
*   SSL Certificates: `cleanmybelly/infra/shared/networking/terraform.tfstate`
*   Dev Backend: `cleanmybelly/infra/environments/dev/backend/terraform.tfstate`
*   Dev Frontend: `cleanmybelly/infra/environments/dev/frontend/terraform.tfstate`
*   Prod Backend: `cleanmybelly/infra/environments/prod/backend/terraform.tfstate`
*   Prod Frontend: `cleanmybelly/infra/environments/prod/frontend/terraform.tfstate`

### C. Backend Output Sharing (Cross-State Reference)
To configure the frontend client with the correct API URL, the frontend Terraform configuration can read the backend state:

```hcl
data "terraform_remote_state" "backend" {
  backend = "s3"
  config = {
    bucket       = "<YOUR_GENERATED_BUCKET_NAME>"
    key          = "cleanmybelly/infra/environments/${var.environment}/backend/terraform.tfstate"
    region       = "us-east-1"
    profile      = "terraform-user"
  }
}

# The frontend can then reference:
# data.terraform_remote_state.backend.outputs.api_gateway_url
```

### D. Security and Least Privilege
*   All DynamoDB tables should run in `PAY_PER_REQUEST` (On-Demand) mode.
*   Configure CloudFront with Origin Access Control (OAC) to ensure the static S3 bucket only accepts requests coming from your CDN distribution, blocking any direct public access to the bucket.
