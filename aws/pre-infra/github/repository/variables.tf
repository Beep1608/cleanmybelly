variable "github_token" {
  type        = string
  description = "GitHub Personal Access Token (PAT) with repo scope"
  sensitive   = true
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

variable "github_repo_visibility" {
  type        = string
  description = "Visibility of the GitHub repository (public or private)"
  default     = "public"
}

variable "project_name" {
  type        = string
  description = "Project name"
  default     = "cleanmybelly"
}
