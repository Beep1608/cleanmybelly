# Pre-Infrastructure Setup Guides (cleanmybelly)

This directory is divided into two decoupled Terraform modules to bootstrap the AWS environment step-by-step:

1. **Bootstrap (`aws/pre-infra/bootstrap`)**: Creates the remote S3 bucket for storing the Terraform state of the main infrastructure components, and the programmatic deployer user (`terraform-deployer`) used locally.
2. **GitHub OIDC & Repository Setup (`aws/pre-infra/github`)**: Contains three decoupled local phases to set up the GitHub repository, provision the OpenID Connect (OIDC) Identity Provider trust link in AWS, configure repository secrets, and publish the deployment workflow file.

---

## Important Security Warning (Local State Files)

> **WARNING:**
> 1. Both directories (`bootstrap` and the three phases inside `github`) run **locally** on your computer.
> 2. Their respective state files (`terraform.tfstate` and `terraform.tfstate.backup`) are stored inside their folder on your machine and are added to `.gitignore`.
> 3. **Do not delete these local state files.** If deleted, Terraform loses track of the resources (the S3 bucket, OIDC provider, IAM roles, GitHub repository parameters, and workflow file), making updates or destruction impossible. It is highly recommended to store a backup of these files in a secure credential vault or password manager.

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

## 2. Deploying Phase 2: GitHub Repository, AWS OIDC Setup, and Repository Secrets (CI/CD Federated Trust)

This step automates the GitHub repository management, AWS setup required for secure, keyless GitHub Actions deployments using OpenID Connect, repository secrets creation, and deployment of the frontend CI/CD workflow.

### A. Phase 1: Repository Setup
1. Navigate to the repository folder:
   ```bash
   cd aws/pre-infra/github/repository
   ```
2. Verify or update the default parameters in `variables.tf`:
   * `github_org_or_username`: Your GitHub account or organization (default: `Beep1608`).
   * `github_repo_name`: The repository name (default: `cleanmybelly`).
3. Run the Terraform command supplying your GitHub Personal Access Token (PAT):
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```
   *(Note: If the repository already exists, you must import it into Terraform state to avoid duplicate resource errors: `terraform import github_repository.repo cleanmybelly`)*

### B. Phase 2: OIDC Setup (AWS Identity Federation)
1. Navigate to the OIDC directory:
   ```bash
   cd ../oidc
   ```
2. Run the Terraform command (it will automatically retrieve the repository name from the Phase 1 local state):
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```

### C. Phase 3: Secrets & Workflow Setup (GitHub Actions Orchestration)
1. Navigate to the secrets-workflow directory:
   ```bash
   cd ../secrets-workflow
   ```
2. Run the Terraform command (providing your GitHub PAT as in Phase 1):
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```
   *(This phase automatically reads the repository name from Phase 1 and the IAM role ARN from Phase 2, creates the `AWS_ROLE_TO_ASSUME` secret in the repository, and publishes the `.github/workflows/deploy-frontend.yml` file to the main branch).*
