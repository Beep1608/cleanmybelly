variable "project_name" {
  type        = string
  description = "Agnostic project or funnel code identifier"
}

variable "environment" {
  type        = string
  description = "Execution environment (e.g., dev, prod, staging)"
}

variable "domain_name" {
  type        = string
  description = "Custom domain name for the frontend (e.g. cleanmybelly.com)"
}

variable "hosted_zone_name" {
  type        = string
  description = "Route 53 hosted zone name (e.g. cleanmybelly.com)"
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM Certificate ARN for the CloudFront custom domain. Must be in us-east-1."
}
