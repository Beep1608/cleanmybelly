variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Name of the project"
  default     = "cleanmybelly"
}

variable "domain_name" {
  type        = string
  description = "Custom domain name for the prod frontend"
  default     = "cleanmybelly.com"
}

variable "hosted_zone_name" {
  type        = string
  description = "Route 53 hosted zone name"
  default     = "cleanmybelly.com"
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM Certificate ARN for the prod CloudFront distribution (must be in us-east-1)"
  default     = "<YOUR_PROD_ACM_CERTIFICATE_ARN>"
}
