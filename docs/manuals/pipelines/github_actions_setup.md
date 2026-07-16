# GitHub Actions Setup Guide (AWS OIDC Federation)

This guide provides step-by-step instructions to configure GitHub Actions with AWS using OpenID Connect (OIDC). This configuration allows GitHub to securely deploy files to your Amazon S3 bucket and invalidate the CloudFront CDN cache without storing permanent AWS Access Keys in your repository.

---

## Prerequisites

1. An **AWS Account** with administrative permissions to manage IAM.
2. A **GitHub Repository** containing your `cleanmybelly` project.
3. AWS CLI installed and configured locally (optional, for CLI-based setup).

---

## Step 1: Create the OIDC Identity Provider in AWS

First, AWS needs to trust GitHub as an Identity Provider (IdP).

1. Log in to the **AWS Management Console** and navigate to the **IAM Console**.
2. In the navigation pane, click **Identity Providers** and then click **Add provider**.
3. Configure the provider settings:
   * **Provider type**: Select **OpenID Connect**.
   * **Provider URL**: Enter `https://token.actions.githubusercontent.com`. Click **Get thumbprint** to verify the URL.
   * **Audience**: Enter `sts.amazonaws.com`.
4. Click **Add provider**.

---

## Step 2: Create the IAM Role for GitHub Actions

Next, you need to create an IAM role that GitHub Actions will assume during execution. This role must trust the OIDC provider created in Step 1.

### Option A: Create via AWS Web Console
1. In the **IAM Console**, click **Roles** -> **Create role**.
2. Select **Custom trust policy** as the trusted entity type.
3. Paste the following JSON policy, replacing `<YOUR_GITHUB_ORG_OR_USERNAME>` with your GitHub account/organization name, and `<YOUR_REPO_NAME>` with `cleanmybelly` (or your repository name):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<YOUR_AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<YOUR_GITHUB_ORG_OR_USERNAME>/<YOUR_REPO_NAME>:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

> **NOTE:**
> The `repo:<ORG>/<REPO>:ref:refs/heads/main` condition restricts role assumption so that only commits pushed to the `main` branch can deploy the infrastructure, protecting you from malicious pull requests.

4. Click **Next**.
5. In **Add permissions**, click **Create policy** (which opens in a new tab) to define the permissions for the deployment. Use the following JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformRemoteStateAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::cleanmybelly-tfstate-v1-*",
        "arn:aws:s3:::cleanmybelly-tfstate-v1-*/*"
      ]
    },
    {
      "Sid": "FrontendS3Deployment",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::cleanmybelly-*-frontend-*",
        "arn:aws:s3:::cleanmybelly-*-frontend-*/*"
      ]
    },
    {
      "Sid": "CloudFrontCacheInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation"
      ],
      "Resource": "*"
    }
  ]
}
```

6. Name this policy `github-actions-deployer-policy` and save it.
7. Return to the Role creation tab, refresh the policies list, select `github-actions-deployer-policy`, and click **Next**.
8. Name the IAM Role `github-actions-deployer-role`.
9. Click **Create role** and copy the **Role ARN** (e.g., `arn:aws:iam::123456789012:role/github-actions-deployer-role`).

---

### Option B: Create via Terraform (Automated IaC - Recommended)

If you prefer to automate the entire process (creating the repository, provisioning OIDC trust on AWS, setting up repository secrets, and creating the workflow file) using Infrastructure as Code (IaC), you can use the multi-phase Terraform setup located under `aws/pre-infra/github`.

#### What does this automation do under the hood?

This setup is divided into three sequential local phases:
1. **Phase 1: Repository (`aws/pre-infra/github/repository`)**: Provisions or manages the GitHub repository using the official GitHub provider.
2. **Phase 2: OIDC Identity Provider (`aws/pre-infra/github/oidc`)**: Creates an IAM OIDC provider for `https://token.actions.githubusercontent.com` and provisions the `github-actions-deployer-role` with a trust policy referencing the repository dynamically using `terraform_remote_state` from Phase 1.
3. **Phase 3: Secrets & Workflow (`aws/pre-infra/github/secrets-workflow`)**: Automates setting up the `AWS_ROLE_TO_ASSUME` secret in the GitHub repository and deploys the `.github/workflows/deploy-frontend.yml` workflow file directly into the repository using the GitHub provider.

#### Deployment Steps:

1. **Configure variables**: 
   * In `aws/pre-infra/github/repository/variables.tf`, ensure the default values for `github_org_or_username` and `github_repo_name` are correct.
   * Provide a GitHub Personal Access Token (PAT) with `repo` scope to the `github_token` variable (via a `terraform.tfvars` file or environment variable `TF_VAR_github_token`).

2. **Phase 1: Run Repository provisioning**:
   ```bash
   cd aws/pre-infra/github/repository
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```
   *(Note: If the repository already exists, you can import it into the state using: `terraform import github_repository.repo <repo-name>`)*

3. **Phase 2: Run AWS OIDC provisioning**:
   ```bash
   cd ../oidc
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```

4. **Phase 3: Run Secrets & Workflow provisioning**:
   ```bash
   cd ../secrets-workflow
   terraform init
   # Ensure TF_VAR_github_token or terraform.tfvars is configured
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```


---

## Step 3: Configure GitHub Repository Secrets

Although OIDC removes the need for AWS access key secrets, you still need to supply the IAM Role ARN to your workflow.

1. In your GitHub repository, go to **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret**.
3. Create the following secret:
   * **Name**: `AWS_ROLE_TO_ASSUME`
   * **Value**: Paste the ARN of the IAM role created in Step 2 (e.g., `arn:aws:iam::123456789012:role/github-actions-deployer-role`).
4. Click **Add secret**.

---

## Step 4: Write the Workflow file

1. In the root of your project, create the following directory path:
   ```bash
   mkdir -p .github/workflows
   ```
2. Create a file named `deploy-frontend.yml` under `.github/workflows/`.
3. Copy the workflow YAML configuration from [github_actions_monorepo.md](../../manuals/pipelines/github_actions_monorepo.md).
4. Update the `role-to-assume` line in the workflow file to point to your secret:
   ```yaml
   role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
   ```

---

## Step 5: Test the Pipeline

1. Ensure your static frontend files exist under a `/app/frontend` directory in your workspace.
2. Commit and push the new workflow to your repository:
   ```bash
   git add .github/workflows/deploy-frontend.yml
   git commit -m "ci: configure frontend github actions deployment pipeline"
   git push origin main
   ```
3. Navigate to the **Actions** tab on your GitHub repository page.
4. Click on the running workflow to verify each stage completes successfully:
   * Code Checkout.
   * Node.js initialization & caching.
   * Compiling assets via `npm run build`.
   * Authenticating to AWS.
   * Fetching Terraform bucket names dynamically.
   * Uploading files to S3.
   * Invalidate CloudFront cache.
