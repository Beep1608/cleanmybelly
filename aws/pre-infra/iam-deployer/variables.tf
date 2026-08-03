variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project used for tagging and resource prefixes"
  type        = string
  default     = "cleanmybelly"
}
