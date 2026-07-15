# GitHub Actions CI/CD Frontend Pipeline for Monorepo (Path-Based Deployment)

This manual provides the architectural overview and a reusable YAML workflow configuration to build and deploy your frontend application located in a monorepo folder (e.g. `/frontend`) to AWS S3, and invalidate the CloudFront cache automatically using path-based triggers.

---

## 1. Pipeline Trigger Strategy (Monorepo Optimization)

In a monorepo containing frontend, backend, and infrastructure code, running the entire pipeline for every commit slows down execution and increases GitHub Actions billable minutes.

We use **Path-Based Triggering (`paths`)** to ensure this frontend pipeline runs **only** when files inside `/frontend` or the workflow itself change:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
```

---

## 2. Reusable GitHub Actions Workflow (`deploy-frontend.yml`)

Create a file at `.github/workflows/deploy-frontend.yml` and paste the following configuration:

```yaml
name: Deploy Frontend App

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'

permissions:
  id-token: write # Required for OIDC AWS Authentication
  contents: read  # Required for checkout

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      # Step 1: Checkout Repository
      - name: Checkout Code
        uses: actions/checkout@v4

      # Step 2: Install Node.js & Restore Cache
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: './frontend/package-lock.json'

      # Step 3: Install & Compile Next.js Frontend
      - name: Build Application
        run: |
          cd frontend
          npm ci
          npm run build # Generates the /out folder with static HTML/CSS/JS export

      # Step 4: Authenticate with AWS via OIDC (No persistent access keys)
      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-deployer-role
          aws-region: us-east-1

      # Step 5: Read S3 Bucket Name and CloudFront ID dynamically from Terraform State
      # This guarantees that if you rename resources in Terraform, the pipeline won't break.
      - name: Extract Terraform Outputs
        id: tf_outputs
        run: |
          cd aws/infra/environments/dev/frontend
          terraform init
          S3_BUCKET=$(terraform output -raw s3_bucket_name)
          CF_DIST_ID=$(terraform output -raw cloudfront_distribution_id)
          echo "s3_bucket=$S3_BUCKET" >> $GITHUB_OUTPUT
          echo "cf_dist_id=$CF_DIST_ID" >> $GITHUB_OUTPUT

      # Step 6: Sync Next.js static export assets to S3
      - name: Sync build folder to S3
        run: |
          aws s3 sync ./frontend/out s3://${{ steps.tf_outputs.outputs.s3_bucket }} --delete

      # Step 7: Invalidate CloudFront CDN Cache (Immediate propagation)
      - name: Invalidate CloudFront Cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ steps.tf_outputs.outputs.cf_dist_id }} \
            --paths "/*"
```

---

## 3. Explaining Key Pipeline Steps

### A. AWS OIDC Authentication (Zero-Keys Security)
Instead of storing permanent `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in GitHub repository secrets (where they could be leaked or expire), this workflow uses **OpenID Connect (OIDC)**:
1. GitHub Actions issues a temporary OIDC Token.
2. AWS validates the token against a configured IAM Identity Provider (IdP) for GitHub.
3. AWS grants temporary credentials with a short expiration time (e.g. 1 hour) to assume `github-actions-deployer-role`.
4. *To configure this on AWS, you must run an IAM OIDC Provider configuration for GitHub.*

### B. Dynamically Fetching Terraform Outputs
In **Step 5**, instead of hardcoding bucket names like `cleanmybelly-dev-frontend-12345`, the runner navigates to the environment's Terraform directory, initializes Terraform (which connects to your S3 remote state bucket), and extracts the outputs. 
* This keeps the CI/CD pipeline **100% independent** of the naming conventions chosen during deployment.
* If you replicate this for production, you only need to copy the workflow and change the path to `aws/infra/environments/prod/frontend`.

### C. CloudFront Invalidation
Because CloudFront caches files at edge locations globally to improve performance, files in S3 won't update on users' browsers immediately. The `create-invalidation` command tells CloudFront to immediately flush its cache for the entire website (`/*`), forcing edge servers to fetch the newly uploaded files from S3 on the next user request.
