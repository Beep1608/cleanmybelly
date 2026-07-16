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

variable "github_org_or_username" {
  type        = string
  description = "GitHub username or organization name"
  default     = "Beep1608"
}

variable "github_repo_name" {
  type        = string
  description = "GitHub repository name"
  default     = "cleanmybelly"
}
