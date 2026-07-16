output "repository_name" {
  value       = github_repository.repo.name
  description = "The name of the repository"
}

output "repository_full_name" {
  value       = github_repository.repo.full_name
  description = "The full name of the repository (owner/repo)"
}

output "repository_html_url" {
  value       = github_repository.repo.html_url
  description = "The URL of the repository"
}
