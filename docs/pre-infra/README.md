# Pre-Infrastructure Setup Guides (cleanmybelly)

This directory is divided into two decoupled Terraform modules to bootstrap the AWS environment step-by-step:

1. **Bootstrap (`aws/pre-infra/bootstrap`)**: Creates the remote S3 bucket for storing the Terraform state of the main infrastructure components, and the programmatic deployer user (`terraform-deployer`) used locally.
2. **GitHub OIDC (`aws/pre-infra/github-oidc`)**: Creates the OpenID Connect (OIDC) Identity Provider trust link in AWS and the role assumed by GitHub Actions for automated, passwordless deployments.

---

## Important Security Warning (Local State Files)

> **WARNING:**
> 1. Both directories (`bootstrap` and `github-oidc`) run **locally** on your computer.
> 2. Their respective state files (`terraform.tfstate` and `terraform.tfstate.backup`) are stored inside their folder on your machine and are added to `.gitignore`.
> 3. **Do not delete these local state files.** If deleted, Terraform loses track of the resources (the S3 bucket, OIDC provider, and IAM roles), making updates or destruction impossible. It is highly recommended to store a backup of these files in a secure credential vault or password manager.

---

## 1. Deploying Phase 1: Bootstrap (S3 Bucket & Local Deployer)

This step sets up the secure S3 bucket with versioning and encryption (using native S3 lock features) and creates the local `terraform-deployer` user.

1. Navigate to the bootstrap folder:
   ```bash
   cd aws/pre-infra/bootstrap
   ```

2. Initialize Terraform (using local state backend):
   ```bash
   terraform init
   ```

3. Plan and apply the configuration:
   ```bash
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```

4. Retrieve the outputs and configure your AWS local profile:
   * Get the generated user credentials:
     ```bash
     terraform output -raw deployer_access_key_id
     terraform output -raw deployer_secret_access_key
     ```
   * Configure your local CLI to use this profile named `terraform-user`:
     ```bash
     aws configure --profile terraform-user
     ```
   * Get the bucket name for remote states:
     ```bash
     terraform output -raw terraform_state_bucket_name
     ```

5. Reference this bucket name under `bucket = "<terraform_state_bucket_name>"` in `providers.tf` for all subsequent folders (`dns-zone`, `certificates`, `backend`, `frontend`).

---

## 2. Deploying Phase 2: GitHub Actions OIDC Setup (CI/CD Federated Trust)

This step automates the AWS setup required for secure, keyless GitHub Actions deployments using OpenID Connect.

1. Navigate to the OIDC directory:
   ```bash
   cd aws/pre-infra/github-oidc
   ```

2. Open [variables.tf](../../aws/pre-infra/github-oidc/variables.tf) and verify or update the default parameters for your GitHub account and repository:
   * `github_org_or_username`: Your GitHub org or username (e.g., `Beep1608`).
   * `github_repo_name`: The name of the project repository (e.g., `cleanmybelly`).

3. Initialize and apply the OIDC stack:
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```

4. Copy the output ARN:
   ```bash
   terraform output -raw github_actions_role_arn
   ```

5. Go to your **GitHub Repository Settings** -> **Secrets and variables** -> **Actions** and create a new repository secret:
   * **Name**: `AWS_ROLE_TO_ASSUME`
   * **Value**: *(The role ARN copied in the previous step)*
