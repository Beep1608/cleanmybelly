terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    # Replace bucket value with the bucket name output from aws/pre-infra/bootstrap
    bucket       = "<TERRAFORM_STATE_BUCKET_NAME>"
    key          = "cleanmybelly/pre-infra/github/oidc/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}
