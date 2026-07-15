terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "cleanmybelly-tfstate-v1-bb8f23ca"
    key          = "cleanmybelly/infra/environments/dev/frontend/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
    profile      = "terraform-user"
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "terraform-user"
}
