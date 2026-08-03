output "deployer_access_key_id" {
  description = "Access Key ID for terraform-deployer"
  value       = aws_iam_access_key.deployer_key.id
}

output "deployer_secret_access_key" {
  description = "Secret Access Key for terraform-deployer"
  value       = aws_iam_access_key.deployer_key.secret
  sensitive   = true
}

output "deployer_user_arn" {
  description = "ARN of the terraform-deployer IAM user"
  value       = aws_iam_user.deployer.arn
}
