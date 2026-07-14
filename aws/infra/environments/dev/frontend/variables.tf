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
  description = "Custom domain name for the dev frontend"
  default     = "dev.cleanmybelly.com"
}

variable "hosted_zone_name" {
  type        = string
  description = "Route 53 hosted zone name"
  default     = "cleanmybelly.com"
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM Certificate ARN for the dev CloudFront distribution (must be in us-east-1)"
  default     = "<YOUR_DEV_ACM_CERTIFICATE_ARN>"
}
