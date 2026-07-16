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
