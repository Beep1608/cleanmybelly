output "workflow_file_path" {
  value       = github_repository_file.deploy_frontend_workflow.file
  description = "The path to the created workflow file in the repository"
}
