data "terraform_remote_state" "repository" {
  backend = "local"
  config = {
    path = "../repository/terraform.tfstate"
  }
}

# --------------------------------------------------------------------------
# Step 1: Create the OIDC Identity Provider in AWS
# --------------------------------------------------------------------------
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]

  # Thumbprint of the DigiCert Global Root G2 certificate which signs GitHub's OIDC token
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = {
    Project     = var.project_name
    Description = "Identity Provider for GitHub Actions OIDC federation"
  }
}

# --------------------------------------------------------------------------
# Step 2: Create the IAM Role for GitHub Actions (OIDC Federated Role)
# --------------------------------------------------------------------------
resource "aws_iam_role" "github_actions_deployer" {
  name        = "github-actions-deployer-role"
  description = "Execution role assumed by GitHub Actions to deploy cleanmybelly frontend and query outputs."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${data.terraform_remote_state.repository.outputs.repository_full_name}:ref:refs/heads/main"
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Description = "Trusted role assumed by GitHub Actions main branch pushes"
  }
}

# --------------------------------------------------------------------------
# Create Deployer IAM Policy with least privilege
# --------------------------------------------------------------------------
resource "aws_iam_policy" "github_actions_deployer_policy" {
  name        = "github-actions-deployer-policy"
  description = "Allows S3 sync to frontend bucket, cache invalidation on CloudFront, and read access to S3 Remote State bucket."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "TerraformRemoteStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-tfstate-${var.project_version}-*",
          "arn:aws:s3:::${var.project_name}-tfstate-${var.project_version}-*/*"
        ]
      },
      {
        Sid    = "FrontendS3Deployment"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-*-frontend-*",
          "arn:aws:s3:::${var.project_name}-*-frontend-*/*"
        ]
      },
      {
        Sid    = "CloudFrontCacheInvalidation"
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation",
          "cloudfront:GetInvalidation"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Description = "Least-privilege policy for CI/CD pipeline deployments"
  }
}

# Attach Deployer Policy to Deployer Role
resource "aws_iam_role_policy_attachment" "github_actions_deployer_attach" {
  role       = aws_iam_role.github_actions_deployer.name
  policy_arn = aws_iam_policy.github_actions_deployer_policy.arn
}
