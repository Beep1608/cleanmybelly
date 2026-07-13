# Place your core frontend client-side rendering static infrastructure resources here
# (S3 static bucket, CloudFront distribution, Route 53 records, and ACM integrations)

variable "environment" {
  type        = string
  description = "Environment identifier (e.g. dev, prod)"
}
