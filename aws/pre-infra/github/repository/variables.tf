variable "github_token" {
  type        = string
  description = "GitHub Personal Access Token (PAT) with repo scope"
  sensitive   = true
}

variable "github_org_or_username" {
  type        = string
  description = "GitHub username or organization name"
}

variable "github_repo_name" {
  type        = string
  description = "GitHub repository name"
}

variable "github_repo_visibility" {
  type        = string
  description = "Visibility of the GitHub repository (public or private)"
  default     = "private"
}

variable "project_name" {
  type        = string
  description = "Base name for project resources and tagging"
  default     = "cleanmybelly"
}

variable "aws_region" {
  type        = string
  description = "Synchronized via env-sync"
}
