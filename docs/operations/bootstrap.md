# Operations: Infrastructure Bootstrapping (Phase 0)

This guide documents the bootstrap procedures required to initialize an AWS Account for the **cleanmybelly** project.

> ℹ️ **ARCHITECTURE DESIGN NOTE: STATE MANAGEMENT**
> 1. Only `aws/pre-infra/bootstrap` runs with **local state**, because its sole purpose is to create the initial S3 Remote State bucket (`cleanmybelly-tfstate-v1-*`).
> 2. All subsequent modules—including the IAM Deployer user (`aws/pre-infra/iam-deployer`) and all GitHub integration modules (`aws/pre-infra/github/*`)—store their `.tfstate` safely inside the **S3 Remote State bucket**.
> 3. This guarantees full traceability and enables updating IAM deployer permissions or GitHub settings at any time without risk of losing local state files.

---

## 1. Deploy S3 Remote State Bucket (Nivel 0)

This step provisions the S3 bucket for storing remote Terraform state and native state locking.

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
3. Retrieve the generated bucket name from Terraform outputs:
   ```bash
   terraform output -raw terraform_state_bucket_name
   ```
4. **Global Provider Configuration Update (Find & Replace)**:
   Perform a global Find & Replace across the workspace (`Ctrl+F` or `Ctrl+Shift+F`) replacing all occurrences of `<TERRAFORM_STATE_BUCKET_NAME>` (and legacy placeholders `<YOUR_TFSTATE_BUCKET_NAME>` or `<YOUR_GENERATED_BUCKET_NAME>`) with your actual generated bucket name (e.g. `cleanmybelly-tfstate-v1-abcdef12`). This automatically updates `bucket = "<TERRAFORM_STATE_BUCKET_NAME>"` across all `providers.tf` files and CLI parameters.

---

## 2. Deploy IAM Local Deployer User (Nivel 1)

This step provisions the programmatic `terraform-deployer` user and attaches the deployment permissions policy.

1. Navigate to:
   ```bash
   cd ../iam-deployer
   ```
2. Verify `providers.tf` has the updated S3 state bucket name (replaced globally in Step 1.4).
3. Initialize and apply:
   ```bash
   terraform init
   terraform apply
   ```
4. Retrieve credentials from outputs and configure your local CLI profile named `terraform-user`:
   ```bash
   terraform output -raw deployer_access_key_id
   terraform output -raw deployer_secret_access_key

   aws configure --profile terraform-user
   ```

---

## 3. Deploy GitHub Integration & OIDC Federation (Nivel 1)

This step configures the GitHub repository, provisions the OpenID Connect (OIDC) trust in AWS IAM, and sets up repository secrets for keyless deployment.

> ℹ️ **GitHub PAT Setup**: For instructions on creating a GitHub Personal Access Token with required permissions, see [GitHub PAT Setup Guide](github_pat_setup.md).

### A. Repository Setup
1. Navigate to:
   ```bash
   cd ../github/repository
   ```
2. Verify `providers.tf` has the updated S3 state bucket name (replaced globally in Step 1.4).
3. Initialize and apply (pass your GitHub PAT token):
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
2. Verify `providers.tf` has the updated S3 state bucket name (replaced globally in Step 1.4).
3. Initialize and apply:
   ```bash
   terraform init
   terraform apply -var="terraform_state_bucket_name=<TERRAFORM_STATE_BUCKET_NAME>"
   ```
   *(Reads repository information dynamically from S3 remote state)*.

### C. Secrets & Workflow Setup
1. Navigate to:
   ```bash
   cd ../secrets-workflow
   ```
2. Verify `providers.tf` has the updated S3 state bucket name (replaced globally in Step 1.4).
3. Initialize and apply:
   ```bash
   terraform init
   terraform apply \
     -var="github_token=<YOUR_GITHUB_PAT>" \
     -var="terraform_state_bucket_name=<TERRAFORM_STATE_BUCKET_NAME>"
   ```
   *(Creates the `AWS_ROLE_TO_ASSUME` repository secret and publishes `.github/workflows/deploy-frontend.yml`)*.
