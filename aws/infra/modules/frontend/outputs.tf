output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront CDN distribution"
  value       = aws_cloudfront_distribution.cdn.domain_name
}

output "cloudfront_hosted_zone_id" {
  description = "Hosted zone ID of the CloudFront CDN distribution (always Z2FDTNDATAQYW2)"
  value       = aws_cloudfront_distribution.cdn.hosted_zone_id
}

output "s3_bucket_name" {
  description = "Name of the static assets S3 bucket"
  value       = aws_s3_bucket.frontend.id
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution, useful for CI/CD cache invalidation"
  value       = aws_cloudfront_distribution.cdn.id
}
