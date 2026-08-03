data "terraform_remote_state" "repository" {
  backend = "s3"
  config = {
    bucket = var.terraform_state_bucket_name
    key    = "cleanmybelly/pre-infra/github/repository/terraform.tfstate"
    region = var.aws_region
  }
}

data "terraform_remote_state" "oidc" {
  backend = "s3"
  config = {
    bucket = var.terraform_state_bucket_name
    key    = "cleanmybelly/pre-infra/github/oidc/terraform.tfstate"
    region = var.aws_region
  }
}

resource "github_actions_secret" "aws_role" {
  repository  = data.terraform_remote_state.repository.outputs.repository_name
  secret_name = "AWS_ROLE_TO_ASSUME"
  value       = data.terraform_remote_state.oidc.outputs.github_actions_role_arn
}

resource "github_repository_file" "deploy_frontend_workflow" {
  repository          = data.terraform_remote_state.repository.outputs.repository_name
  branch              = "main"
  file                = ".github/workflows/deploy-frontend.yml"
  content             = <<EOF
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
          npm run build # Generates the /out folder with static HTML/CSS/JS export

      # Step 4: Authenticate with AWS via OIDC (No persistent access keys)
      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: $${{ secrets.AWS_ROLE_TO_ASSUME }}
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
          aws s3 sync ./app/frontend/out s3://$${{ steps.tf_outputs.outputs.s3_bucket }} --delete

      # Step 7: Invalidate CloudFront CDN Cache (Immediate propagation)
      - name: Invalidate CloudFront Cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id $${{ steps.tf_outputs.outputs.cf_dist_id }} \
            --paths "/*"
EOF
  commit_message      = "ci: configure frontend github actions deployment pipeline"
  commit_author       = "Terraform Deployer"
  commit_email        = "terraform-deployer@cleanmybelly.local"
  overwrite_on_create = true
}
