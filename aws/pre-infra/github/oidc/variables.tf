variable "aws_region" {
  type        = string
  description = "AWS region for infrastructure deployment"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Base name for project resources and tagging"
  default     = "cleanmybelly"
}

variable "project_version" {
  type        = string
  description = "Architecture or infrastructure version identifier"
  default     = "v1"
}

variable "terraform_state_bucket_name" {
  type        = string
  description = "Name of the S3 bucket storing Terraform remote state"
}

variable "github_org_or_username" {
  type        = string
  description = "Synchronized via env-sync"
}
