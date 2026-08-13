terraform {
  required_version = ">= 1.10.0"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    key          = "cleanmybelly/pre-infra/github/secrets-workflow/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

provider "github" {
  token = var.github_token
  owner = var.github_org_or_username
}
