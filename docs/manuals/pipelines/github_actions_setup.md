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

If you prefer to automate both **Step 1** and **Step 2** using Infrastructure as Code (IaC), you can use the pre-configured Terraform module located under `aws/pre-infra/github-oidc`.

#### What does this automation do under the hood?

This module deploys the complete secure trust federation between GitHub and your AWS account, doing the following:
1. **Registers the OIDC Identity Provider:** Creates an IAM OIDC provider for `https://token.actions.githubusercontent.com` in your AWS account using the audience `sts.amazonaws.com` and the thumbprint of the DigiCert Global Root G2 certificate (`6938fd4d98bab03faadb97b34396831e3780aea1`) which GitHub uses.
2. **Creates the Federated IAM Role:** Provisions the `github-actions-deployer-role` with a trust relationship policy. This trust policy validates GitHub's OIDC tokens and ensures that **only** workflows running from the `main` branch of your specified repository (`github_org_or_username`/`github_repo_name`) are authorized to assume the role.
3. **Applies Least-Privilege IAM Policies:** Creates and attaches the `github-actions-deployer-policy` containing:
   * **`TerraformRemoteStateAccess`:** Allows GitHub Actions to initialize and read/write the Terraform remote state files in the S3 bucket (`cleanmybelly-tfstate-v1-*`).
   * **`FrontendS3Deployment`:** Allows sync operations (uploading assets, deleting deprecated files) to the frontend hosting bucket (`cleanmybelly-*-frontend-*`).
   * **`CloudFrontCacheInvalidation`:** Allows cache invalidations so that static file updates propagate immediately.

#### Deployment Steps:

1. **Configure variables**: Open the variables file [aws/pre-infra/github-oidc/variables.tf](../../../aws/pre-infra/github-oidc/variables.tf) and verify or update the default values for your repository details:
   ```hcl
   variable "github_org_or_username" {
     type        = string
     default     = "Beep1608"
   }

   variable "github_repo_name" {
     type        = string
     default     = "cleanmybelly"
   }
   ```
2. **Execute Terraform**: Navigate to the OIDC directory and run apply:
   ```bash
   cd aws/pre-infra/github-oidc
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```
3. **Get Role ARN**: Terraform will output the ARN of the created role as `github_actions_role_arn`. Copy this value.

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
