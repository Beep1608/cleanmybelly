output "cloudfront_domain_name" {
  description = "Domain name of the CDN distribution"
  value       = module.frontend.cloudfront_domain_name
}

output "s3_bucket_name" {
  description = "Name of the static hosting S3 bucket"
  value       = module.frontend.s3_bucket_name
}
