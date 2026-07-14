terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "<YOUR_GENERATED_BUCKET_NAME>"
    key          = "cleanmybelly/infra/shared/networking/terraform.tfstate"
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

# CloudFront certificates must be in us-east-1
provider "aws" {
  alias   = "us_east_1"
  region  = "us-east-1"
  profile = "terraform-user"
}
