# Operations: GitHub OIDC Trust Verification & Policy Reference

This document serves as an auditing reference for verifying the AWS OpenID Connect (OIDC) Identity Provider trust link and IAM deployer role created by Terraform.

> ℹ️ **Automated IaC Note**:
> The OIDC Identity Provider and IAM role are provisioned automatically via Terraform in `aws/pre-infra/github`. You do **not** need to create these manually in the AWS Console. This document exists for security auditing and verifying policy compliance.

---

## 1. IAM Role Trust Policy Spec

The `github-actions-deployer-role` uses the following trust relationship policy:

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
          "token.actions.githubusercontent.com:sub": "repo:<YOUR_GITHUB_ORG_OR_USERNAME>/cleanmybelly:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

---

## 2. IAM Role Deployment Permissions Policy Spec

The deployment policy (`github-actions-deployer-policy`) attached to the role defines least-privilege permissions:

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

---

## 3. GitHub Repository Secret Verification

Verify that your GitHub Repository contains the following Secret under **Settings** -> **Secrets and variables** -> **Actions**:

| Secret Name | Value Example | Description |
| :--- | :--- | :--- |
| `AWS_ROLE_TO_ASSUME` | `arn:aws:iam::123456789012:role/github-actions-deployer-role` | Role ARN assumed dynamically during GitHub Actions runs. |
