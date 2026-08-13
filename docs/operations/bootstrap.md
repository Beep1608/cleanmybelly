# Operations: Infrastructure Bootstrapping (Phase 0)

This guide documents the bootstrap procedures required to initialize an AWS Account for the **cleanmybelly** project.

> ℹ️ **ARCHITECTURE DESIGN NOTE: STATE MANAGEMENT**
> 1. Only `aws/pre-infra/bootstrap` runs with **local state**, because its sole purpose is to create the initial S3 Remote State bucket (`cleanmybelly-tfstate-v1-*`).
> 2. All subsequent modules—including the IAM Deployer user (`aws/pre-infra/iam-deployer`) and all GitHub integration modules (`aws/pre-infra/github/*`)—store their `.tfstate` safely inside the **S3 Remote State bucket**.
> 3. This guarantees full traceability and enables updating IAM deployer permissions or GitHub settings at any time without risk of losing local state files.
> 4. Dynamic backend initialization is handled by `tools/env_sync.py`, which generates `backend.tfbackend` files locally for use with `terraform init -backend-config=backend.tfbackend`.

---

## 1. Deploy S3 Remote State Bucket (Level 0)

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
4. **Environment Configuration & Backend Synchronization (`env-sync`)**:
   Open `environments/global/.env.pre-infra` and update:
   ```ini
   [*]
   !terraform_state_bucket = "<GENERATED_BUCKET_NAME>"

   [github/oidc | github/secrets-workflow]
   terraform_state_bucket_name = "<GENERATED_BUCKET_NAME>"
   ```
   Execute the synchronizer from the repository root:
   ```bash
   cd ../../../
   python3 tools/env_sync.py
   ```
   This generates `backend.tfbackend` and `terraform.tfvars` across all modules without modifying tracked git files.

---

## 2. Deploy IAM Local Deployer User (Level 1)

This step provisions the programmatic `terraform-deployer` user and attaches the deployment permissions policy.

1. Navigate to:
   ```bash
   cd aws/pre-infra/iam-deployer
   ```
2. Initialize and apply using the generated backend config:
   ```bash
   terraform init -backend-config=backend.tfbackend
   terraform apply
   ```
3. Retrieve credentials from outputs and configure your local CLI profile named `terraform-user`:
   ```bash
   terraform output -raw deployer_access_key_id
   terraform output -raw deployer_secret_access_key

   aws configure --profile terraform-user
   ```

---

## 3. Deploy GitHub Integration & OIDC Federation (Level 1)

This step configures the GitHub repository, provisions the OpenID Connect (OIDC) trust in AWS IAM, and sets up repository secrets for keyless deployment.

> ℹ️ **GitHub PAT Setup**: For instructions on creating a GitHub Personal Access Token with required permissions, see [GitHub PAT Setup Guide](github_pat_setup.md).

### A. Repository Setup
1. Navigate to:
   ```bash
   cd ../github/repository
   ```
2. Initialize and apply (pass your GitHub PAT token or ensure it is set in `.env.pre-infra`):
   ```bash
   terraform init -backend-config=backend.tfbackend
   terraform apply
   ```
   *(If the repository already exists on GitHub, import it into Terraform state: `terraform import github_repository.repo cleanmybelly`)*.
3. Retrieve the new repository HTML URL:
   ```bash
   terraform output -raw repository_html_url
   ```

### B. Connect Local Clone to Provisioned Repository
> ℹ️ **CRITICAL STEP**: The newly provisioned GitHub repository is created empty. Before deploying OIDC federation and workflow secrets in subsequent steps, you must point your local git remote to your new repository and push the codebase so the `main` branch exists on GitHub.

1. Update local git remote origin URL:
   ```bash
   git remote set-url origin <NEW_REPOSITORY_URL>.git
   ```
2. Push full codebase to main branch:
   ```bash
   git push -u origin main
   ```

### C. AWS OIDC Setup
1. Navigate to:
   ```bash
   cd ../oidc
   ```
2. Initialize and apply:
   ```bash
   terraform init -backend-config=backend.tfbackend
   terraform apply
   ```
   *(Reads repository information dynamically from S3 remote state)*.

### D. Secrets & Workflow Setup
1. Navigate to:
   ```bash
   cd ../secrets-workflow
   ```
2. Initialize and apply:
   ```bash
   terraform init -backend-config=backend.tfbackend
   terraform apply
   ```
   *(Creates the `AWS_ROLE_TO_ASSUME` repository secret and publishes `.github/workflows/deploy-frontend.yml`)*.
