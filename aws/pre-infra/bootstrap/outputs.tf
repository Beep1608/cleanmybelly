output "deployer_access_key_id" {
  description = "Access Key ID for terraform-deployer"
  value       = aws_iam_access_key.deployer_key.id
}

output "deployer_secret_access_key" {
  description = "Secret Access Key for terraform-deployer"
  value       = aws_iam_access_key.deployer_key.secret
  sensitive   = true
}

output "terraform_state_bucket_name" {
  description = "Generated standardized name for the S3 backend bucket"
  value       = aws_s3_bucket.terraform_state.bucket
}