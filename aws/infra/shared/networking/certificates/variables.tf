variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "hosted_zone_name" {
  type        = string
  description = "Parent Route 53 hosted zone name (e.g., cleanmybelly.com)"
  default     = "cleanmybelly.com"
}
