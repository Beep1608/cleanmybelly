# Getting Started: Complete Infrastructure Deployment Guide

This guide provides an end-to-end, linear walkthrough for spinning up the entire **cleanmybelly** cloud ecosystem on AWS from scratch. Follow these steps in sequential order.

---

## Deployment Lifecycle Map

```mermaid
graph TD
    Step0[Step 0: Prerequisites & Environment Preparation] --> Step1[Step 1: Account Bootstrap & OIDC Trust]
    Step1 --> Step1_5[Step 1.5: Connect Local Clone to Provisioned Repository]
    Step1_5 --> Step2[Step 2: DNS Hosted Zone]
    Step2 --> Step3[Step 3: Namecheap Domain Delegation]
    Step3 --> Step4[Step 4: ACM SSL Certificates]
    Step4 --> Step5[Step 5: Backend Infrastructure]
    Step5 --> Step6[Step 6: Frontend Infrastructure]
    Step6 --> Step7[Step 7: SSM Secrets Setup]
    Step7 --> Step8[Step 8: CI/CD Pipeline Deployment]
```

---

## Step 0: Prerequisites & Environment Preparation

Before executing any Terraform commands, verify you have the following installed on your machine:
1. **Terraform CLI** (`>= 1.10.0`)
2. **AWS CLI** (`v2`) configured with administrative access to your AWS Account.
3. **GitHub Personal Access Token (PAT)** with `repo` and `workflow` scopes.
   > ℹ️ **PAT Generation Guide**: [docs/operations/github_pat_setup.md](operations/github_pat_setup.md)

> ℹ️ **Automated CLI Alternative**: You can choose to execute Steps 1 through 4 manually following this guide, or automate them using the Python Bootstrap CLI tool (`python3 tools/bootstrap.py`). For details on the automated CLI tool, see [Bootstrap CLI Tool Reference](reference/bootstrap_cli.md).

---

## Step 1: Bootstrap Remote State & GitHub OIDC Trust

> ℹ️ **Detailed Operations Guides**: [Bootstrap Guide](operations/bootstrap.md) | [GitHub PAT Setup Guide](operations/github_pat_setup.md)

1. **Bootstrap S3 Remote State Bucket**:
   ```bash
   cd aws/pre-infra/bootstrap
   terraform init
   terraform apply
   ```
   * Retrieve the generated S3 remote state bucket name:
     ```bash
     terraform output -raw terraform_state_bucket_name
     ```

2. **Global Provider Configuration Update (Find & Replace)**:
   > ℹ️ **CRITICAL**: Only `aws/pre-infra/bootstrap` uses local state. All other modules store state in S3.
   * Open your IDE's Find & Replace tool (`Ctrl+F` or `Ctrl+Shift+F`).
   * Search across the workspace for `<TERRAFORM_STATE_BUCKET_NAME>` (including legacy placeholders `<YOUR_TFSTATE_BUCKET_NAME>` and `<YOUR_GENERATED_BUCKET_NAME>`).
   * Replace all occurrences with your actual generated bucket name (e.g. `cleanmybelly-tfstate-v1-abcdef12`).
   * This automatically updates `bucket = "<TERRAFORM_STATE_BUCKET_NAME>"` across all `providers.tf` files and CLI parameters project-wide.

3. **Deploy IAM Local Deployer User**:
   ```bash
   cd ../iam-deployer
   terraform init
   terraform apply
   ```
   * Configure local AWS CLI profile named `terraform-user` using outputs:
     ```bash
     aws configure --profile terraform-user
     ```

4. **Provision GitHub Repository**:
   ```bash
   cd ../github/repository
   terraform init
   terraform apply -var="github_token=<YOUR_GITHUB_PAT>"
   ```
   * Retrieve the new repository HTML URL:
     ```bash
     terraform output -raw repository_html_url
     ```

---

## Step 1.5: Connect Local Clone to Provisioned Repository

> ℹ️ **CRITICAL STEP**: The newly provisioned GitHub repository is created empty. Before deploying OIDC federation and workflow secrets in subsequent steps, you must point your local git remote to your new repository and push the codebase so the `main` branch exists on GitHub.

1. Update your local git remote origin to point to your new GitHub repository:
   ```bash
   git remote set-url origin <NEW_REPOSITORY_URL>.git
   # Example: git remote set-url origin https://github.com/JoseLopezLara/cleanmybelly.git
   ```

2. Push the full codebase to the `main` branch of your new repository:
   ```bash
   git push -u origin main
   ```

3. Deploy OIDC Federation & Workflow Secrets:
   ```bash
   # OIDC Federation Setup
   cd ../oidc
   terraform init
   terraform apply -var="terraform_state_bucket_name=<TERRAFORM_STATE_BUCKET_NAME>"

   # Repository Secrets & Workflow Publishing
   cd ../secrets-workflow
   terraform init
   terraform apply \
     -var="github_token=<YOUR_GITHUB_PAT>" \
     -var="terraform_state_bucket_name=<TERRAFORM_STATE_BUCKET_NAME>"
   ```

---

## Step 2: Provision Route 53 DNS Zone

> ℹ️ **Architecture Overview**: [docs/architecture/aws_services.md](architecture/aws_services.md#1-amazon-route-53)

1. Verify that `aws/infra/shared/networking/dns-zone/providers.tf` has the updated S3 state bucket name (replaced in Step 1.2).
2. Deploy the DNS zone:
   ```bash
   cd aws/infra/shared/networking/dns-zone
   terraform init
   terraform apply
   ```
3. Copy the 4 **Name Servers** (`name_servers`) returned in the Terraform outputs.

---

## Step 3: Delegate Custom Domain (Registrar Setup)

> ℹ️ **Detailed Operations Guide**: [docs/operations/dns_delegation.md](operations/dns_delegation.md)

1. Log into your registrar (e.g. Namecheap) and set your domain's DNS to **Custom DNS**.
2. Paste the 4 AWS Name Servers retrieved from Step 2 and save.
3. Verify DNS propagation using terminal `dig`:
   ```bash
   dig cleanmybelly.com NS
   ```

---

## Step 4: Request & Validate ACM SSL Certificates

1. Verify that `aws/infra/shared/networking/certificates/providers.tf` has the updated S3 state bucket name (replaced in Step 1.2).
2. Request and auto-validate certificates:
   ```bash
   cd aws/infra/shared/networking/certificates
   terraform init
   terraform apply
   ```
   *(ACM validation completes automatically in 2–5 minutes via Route 53 CNAME records).*

---

## Step 5: Deploy Backend Environment (`dev` or `prod`)

> ℹ️ **Architecture Overview**: [docs/architecture/backend.md](architecture/backend.md)

1. Navigate to the environment folder:
   ```bash
   cd aws/infra/environments/dev/backend
   ```
2. Verify that `providers.tf` has the updated S3 state bucket name (replaced in Step 1.2).
3. Verify or update the Lambda zip package path in `main.tf`:
   ```hcl
   lambda_zip_path = "${path.module}/../../../../backend/dist/function.zip"
   ```
4. Deploy backend resources (Lambda, API Gateway, DynamoDB):
   ```bash
   terraform init
   terraform apply
   ```

---

## Step 6: Deploy Frontend Environment (`dev` or `prod`)

> ℹ️ **Architecture Overview**: [docs/architecture/frontend.md](architecture/frontend.md)

1. Navigate to the environment folder:
   ```bash
   cd aws/infra/environments/dev/frontend
   ```
2. Verify that `providers.tf` has the updated S3 state bucket name (replaced in Step 1.2).
3. Deploy static hosting and CloudFront CDN:
   ```bash
   terraform init
   terraform apply
   ```

---

## Step 7: Configure Application Secrets in SSM

> ℹ️ **Detailed Operations Guide**: [docs/operations/secrets_management.md](operations/secrets_management.md)

Add required application secrets to AWS Systems Manager Parameter Store:
```bash
aws ssm put-parameter \
  --name "/cleanmybelly/dev/stripe_secret_key" \
  --value "sk_test_..." \
  --type "SecureString" \
  --overwrite \
  --profile terraform-user
```

---

## Step 8: Verify Automated CI/CD Pipeline

> ℹ️ **Pipeline Details**: [docs/reference/github_actions_monorepo.md](reference/github_actions_monorepo.md)

1. Build your frontend application locally:
   ```bash
   cd app/frontend
   npm ci && npm run build
   ```
2. Push your changes to `main` branch to trigger `.github/workflows/deploy-frontend.yml`.
3. Check the GitHub Actions execution log to confirm successful asset sync and CloudFront CDN invalidation.
