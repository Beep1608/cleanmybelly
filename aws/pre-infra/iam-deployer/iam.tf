resource "aws_iam_user" "deployer" {
  name = "terraform-deployer"
  path = "/system/"

  tags = {
    Project     = var.project_name
    Description = "Programmatic user for CI/CD and Terraform deployment"
  }
}

resource "aws_iam_access_key" "deployer_key" {
  user = aws_iam_user.deployer.name
}

resource "aws_iam_policy" "deployer_policy" {
  name        = "TerraformDeployerPolicyV1"
  path        = "/"
  description = "Policy for serverless architecture deployments including S3, CloudFront, Route53, ACM, API Gateway, Lambda, DynamoDB, CloudWatch Logs, and IAM roles."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "v1ArchitectureDeployer"
        Effect = "Allow"
        Action = [
          "lambda:*",
          "apigateway:*",
          "dynamodb:*",
          "s3:*",
          "route53:*",
          "acm:*",
          "cloudfront:*",
          "logs:*",
          "iam:CreateServiceLinkedRole",
          "iam:CreateInstanceProfile",
          "iam:GetInstanceProfile",
          "iam:DeleteInstanceProfile",
          "iam:AddRoleToInstanceProfile",
          "iam:RemoveRoleFromInstanceProfile",
          "iam:PassRole",
          "iam:CreateRole",
          "iam:GetRole",
          "iam:DeleteRole",
          "iam:UpdateRole",
          "iam:UpdateRoleDescription",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:AttachRolePolicy",
          "iam:PutRolePolicy",
          "iam:GetRolePolicy",
          "iam:DetachRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "deployer_attach" {
  user       = aws_iam_user.deployer.name
  policy_arn = aws_iam_policy.deployer_policy.arn
}
