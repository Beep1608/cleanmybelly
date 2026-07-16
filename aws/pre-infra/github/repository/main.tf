resource "github_repository" "repo" {
  name        = var.github_repo_name
  description = "Clean My Belly project repository"
  visibility  = var.github_repo_visibility

  has_issues   = true
  has_projects = true
  has_wiki     = true

  # Set up auto-initialization settings if needed, but since it is imported/created, we keep it simple.
  auto_init = false
}
