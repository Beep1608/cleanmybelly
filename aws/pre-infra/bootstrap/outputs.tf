output "terraform_state_bucket_name" {
  description = "Generated standardized name for the S3 backend bucket"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "terraform_state_bucket_arn" {
  description = "ARN of the S3 backend bucket"
  value       = aws_s3_bucket.terraform_state.arn
}