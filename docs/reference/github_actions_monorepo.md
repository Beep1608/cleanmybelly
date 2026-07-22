# Reference: Monorepo GitHub Actions Pipeline Specification

This reference document outlines the path-triggered CI/CD workflow configuration used to build Next.js static assets and deploy them to Amazon S3 and CloudFront.

---

## 1. Path-Based Triggering Strategy

To prevent unnecessary pipeline runs when updating backend or documentation code, the workflow triggers **only** when files inside `app/frontend/` or the workflow itself change:

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'app/frontend/**'
      - '.github/workflows/deploy-frontend.yml'
```

---

## 2. Full Workflow Blueprint (`deploy-frontend.yml`)

The production workflow file is located at `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend App

on:
  push:
    branches:
      - main
    paths:
      - 'app/frontend/**'
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
          cache-dependency-path: './app/frontend/package-lock.json'

      # Step 3: Install & Compile Next.js Frontend
      - name: Build Application
        run: |
          cd app/frontend
          npm ci
          npm run build # Exports static HTML/CSS/JS to /out

      # Step 4: Authenticate with AWS via OIDC (No permanent access keys)
      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
          aws-region: us-east-1

      # Step 5: Read S3 Bucket Name and CloudFront ID dynamically from Terraform State
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
          aws s3 sync ./app/frontend/out s3://${{ steps.tf_outputs.outputs.s3_bucket }} --delete

      # Step 7: Invalidate CloudFront CDN Cache (Immediate propagation)
      - name: Invalidate CloudFront Cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ steps.tf_outputs.outputs.cf_dist_id }} \
            --paths "/*"
```
