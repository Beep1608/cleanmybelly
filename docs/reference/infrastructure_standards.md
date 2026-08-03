# Reference: Infrastructure Directory & State Standards

This reference document outlines the directory structure, environment segregation, state key hierarchy, and architectural conventions for the **cleanmybelly** infrastructure codebase under `/aws/infra`.

---

## 1. Directory Structure

```text
aws/
├── pre-infra/
│   ├── bootstrap/                     # Phase 0: S3 Remote State Bucket (Local State)
│   ├── iam-deployer/                  # Phase 0: Local Deployer IAM User (S3 State)
│   └── github/                        # Phase 0: GitHub Integration (S3 State)
│       ├── repository/
│       ├── oidc/
│       └── secrets-workflow/
└── infra/
    ├── modules/
    │   ├── backend/
    │   └── frontend/
    ├── shared/
    │   └── networking/
    │       ├── dns-zone/
    │       └── certificates/
    └── environments/
        ├── dev/
        │   ├── backend/
        │   └── frontend/
        └── prod/
            ├── backend/
            └── frontend/
```

---

## 2. Segmentation Strategy

### Dev vs. Prod Environment Isolation
* **State Keys**: Development (`dev`) and production (`prod`) environments use different S3 state keys.
* **Naming Prefixes**: Resources use distinct prefixes (e.g. `cleanmybelly-dev-*` vs `cleanmybelly-prod-*`).
* **Variable Isolation**: Region, scaling capacities, and domain names are configured per environment in `variables.tf`.

### Frontend vs. Backend Decoupling
* **Decoupled State**: Backend (Lambda, API Gateway, DynamoDB) and Frontend (S3 static bucket, CloudFront) have separate Terraform state files. Visual frontend updates do not alter compute/database infrastructure.
* **Remote State Cross-Referencing**: Frontend configurations pull API Gateway URLs dynamically using `terraform_remote_state`.

---

## 3. Remote State Key Hierarchy

All infrastructure states (except `aws/pre-infra/bootstrap` which creates the bucket) use the S3 backend with native state locking (`use_lockfile = true`):

| Component / Layer | S3 Remote State Key |
| :--- | :--- |
| **IAM Local Deployer** | `cleanmybelly/pre-infra/iam-deployer/terraform.tfstate` |
| **GitHub Repository** | `cleanmybelly/pre-infra/github/repository/terraform.tfstate` |
| **GitHub OIDC Trust** | `cleanmybelly/pre-infra/github/oidc/terraform.tfstate` |
| **GitHub Secrets & Workflow** | `cleanmybelly/pre-infra/github/secrets-workflow/terraform.tfstate` |
| **DNS Zone** | `cleanmybelly/infra/shared/networking/dns-zone/terraform.tfstate` |
| **SSL Certificates** | `cleanmybelly/infra/shared/networking/certificates/terraform.tfstate` |
| **Dev Backend** | `cleanmybelly/infra/environments/dev/backend/terraform.tfstate` |
| **Dev Frontend** | `cleanmybelly/infra/environments/dev/frontend/terraform.tfstate` |
| **Prod Backend** | `cleanmybelly/infra/environments/prod/backend/terraform.tfstate` |
| **Prod Frontend** | `cleanmybelly/infra/environments/prod/frontend/terraform.tfstate` |

---

## 4. Cross-State Reference HCL Example

Frontend code references backend outputs dynamically:

```hcl
data "terraform_remote_state" "backend" {
  backend = "s3"
  config = {
    bucket  = "<TERRAFORM_STATE_BUCKET_NAME>"
    key     = "cleanmybelly/infra/environments/${var.environment}/backend/terraform.tfstate"
    region  = "us-east-1"
    profile = "terraform-user"
  }
}

# Reference syntax in frontend module:
# data.terraform_remote_state.backend.outputs.api_gateway_url
```
