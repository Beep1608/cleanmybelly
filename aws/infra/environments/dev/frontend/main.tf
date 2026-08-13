# Read API Gateway dynamic endpoints and database info from the Backend state file
data "terraform_remote_state" "backend" {
  backend = "s3"
  config = {
    bucket  = var.terraform_state_bucket_name
    key     = "cleanmybelly/infra/environments/dev/backend/terraform.tfstate"
    region  = "us-east-1"
    profile = "terraform-user"
  }
}

# Read Shared Networking outputs (Route 53 hosted zone and SSL certificates)
data "terraform_remote_state" "networking" {
  backend = "s3"
  config = {
    bucket  = var.terraform_state_bucket_name
    key     = "cleanmybelly/infra/shared/networking/terraform.tfstate"
    region  = "us-east-1"
    profile = "terraform-user"
  }
}

module "frontend" {
  source = "../../../modules/frontend"

  environment  = "dev"
  project_name = var.project_name

  # Domain details
  domain_name = "dev.${data.terraform_remote_state.networking.outputs.hosted_zone_name}"

  # SSL/TLS Certificate fetched dynamically
  acm_certificate_arn = data.terraform_remote_state.networking.outputs.dev_frontend_cert_arn
}
