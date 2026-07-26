# Operations: Infrastructure Bootstrapping (Phase 0)

This guide documents the bootstrap procedures required to initialize an AWS Account for the **cleanmybelly** project.

> ⚠️ **IMPORTANT SECURITY WARNING: LOCAL STATE FILES**
> 1. The bootstrap modules located in `aws/pre-infra/bootstrap` and `aws/pre-infra/github/*` run **locally** on your workstation.
> 2. Their state files (`terraform.tfstate`) are saved locally and are ignored by `.gitignore` to prevent secret leakage.
> 3. **Do not delete these local state files.** If deleted, Terraform will lose track of base resources (S3 state bucket, IAM deployer, OIDC identity provider, and GitHub repository configuration). Back up these state files to a secure team vault.

---

## 1. Deploy S3 State Bucket & Local Deployer User

This step provisions the S3 bucket for storing remote Terraform state and creates the programmatic `terraform-deployer` user for local execution.

1. Navigate to the bootstrap directory:
   ```bash
   cd aws/pre-infra/bootstrap
   ```
2. Initialize and apply:
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```
3. Retrieve credentials from Terraform outputs and configure your local CLI profile:
   ```bash
   # Retrieve outputs
   terraform output -raw deployer_access_key_id
   terraform output -raw deployer_secret_access_key
   terraform output -raw terraform_state_bucket_name

   # Configure AWS CLI profile named 'terraform-user'
   aws configure --profile terraform-user
   ```
4. Save the generated bucket name (`terraform_state_bucket_name`). You will reference it in `providers.tf` across all main infrastructure components (`dns-zone`, `certificates`, `backend`, `frontend`).

---

## 2. Deploy GitHub OIDC Trust & CI/CD Federation

This step configures the GitHub repository, provisions the OpenID Connect (OIDC) trust in AWS IAM, and sets up repository secrets for keyless deployment.

### A. Repository Setup
1. Navigate to:
   ```bash
   cd aws/pre-infra/github/repository
   ```
2. Initialize and apply (pass your GitHub PAT token):
   ```bash
   terraform init
   terraform apply -var="github_token=<YOUR_GITHUB_PAT>"
   # Example with full path from repository root and token value:
   # cd <REPO_ROOT>/aws/pre-infra/github/repository && terraform apply -var="github_token=ghp_1234567890abcdefghijklmnopqrstuvwxyz"
   ```
   *(If the repository already exists on GitHub, import it into Terraform state: `terraform import github_repository.repo cleanmybelly`)*.

### B. AWS OIDC Setup
1. Navigate to:
   ```bash
   cd ../oidc
   ```
2. Initialize and apply:
   ```bash
   terraform init
   terraform apply
   ```
   *(This automatically reads repository parameters from the Phase A local state file).*

### C. Secrets & Workflow Setup
1. Navigate to:
   ```bash
   cd ../secrets-workflow
   ```
2. Initialize and apply:
   ```bash
   terraform init
   terraform apply -var="github_token=<YOUR_GITHUB_PAT>"
   # Example with full path from repository root and token value:
   # cd <REPO_ROOT>/aws/pre-infra/github/secrets-workflow && terraform apply -var="github_token=ghp_1234567890abcdefghijklmnopqrstuvwxyz"
   ```
   *(This step creates the `AWS_ROLE_TO_ASSUME` repository secret and publishes the `.github/workflows/deploy-frontend.yml` workflow file).*
