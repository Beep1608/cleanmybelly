variable "github_token" {
  type        = string
  description = "GitHub Personal Access Token (PAT) with repo scope"
  sensitive   = true
}

variable "github_org_or_username" {
  type        = string
  description = "GitHub username or organization name"
}

variable "aws_region" {
  type        = string
  description = "AWS region for infrastructure deployment"
  default     = "us-east-1"
}

variable "terraform_state_bucket_name" {
  type        = string
  description = "Name of the S3 bucket storing Terraform remote state"
}

variable "project_name" {
  type        = string
  description = "Synchronized via env-sync"
}
