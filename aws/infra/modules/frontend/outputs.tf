output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront CDN distribution"
  value       = aws_cloudfront_distribution.cdn.domain_name
}

output "cloudfront_arn" {
  description = "ARN of the CloudFront CDN distribution"
  value       = aws_cloudfront_distribution.cdn.arn
}

output "s3_bucket_name" {
  description = "Name of the static assets S3 bucket"
  value       = aws_s3_bucket.frontend.id
}
