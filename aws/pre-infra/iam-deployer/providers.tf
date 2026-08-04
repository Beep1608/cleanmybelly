terraform {
  required_version = ">= 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    # Replace bucket value with the bucket name output from aws/pre-infra/bootstrap
    bucket       = "cleanmybelly-tfstate-v1-8b543648"
    key          = "cleanmybelly/pre-infra/iam-deployer/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}
