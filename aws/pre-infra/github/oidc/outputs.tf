output "github_actions_role_arn" {
  description = "ARN of the IAM Role created for GitHub Actions OIDC trust. Add this to your GitHub Repository Secrets as AWS_ROLE_TO_ASSUME."
  value       = aws_iam_role.github_actions_deployer.arn
}
