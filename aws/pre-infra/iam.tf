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
  description = "Least privilege policy for v1 architecture deployments. This policy includes EC2, Lambda, API Gateway, S3, Cognito, Route53, Roles management, Policy management and Instance profile management."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "v1ArchitectureDeployer"
        Effect = "Allow"
        Action = [
          "ec2:*",
          "lambda:*",
          "apigateway:*",
          "dynamodb:*",
          "s3:*",
          "iam:CreateInstanceProfile",
          "iam:GetInstanceProfile",
          "iam:DeleteInstanceProfile",
          "iam:AddRoleToInstanceProfile",
          "iam:RemoveRoleFromInstanceProfile",
          "iam:PassRole",
          "iam:CreateRole",
          "iam:GetRole",
          "iam:DeleteRole",
          "iam:AttachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DetachRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole",
          "cognito-idp:*",
          "route53:*"
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