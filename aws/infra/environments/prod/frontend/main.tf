# Read API Gateway dynamic endpoints and database info from the Backend state file
data "terraform_remote_state" "backend" {
  backend = "s3"
  config = {
    bucket  = "<YOUR_GENERATED_BUCKET_NAME>"
    key     = "cleanmybelly/infra/environments/prod/backend/terraform.tfstate"
    region  = "us-east-1"
    profile = "terraform-user"
  }
}

# Read Shared Networking outputs (Route 53 hosted zone and SSL certificates)
data "terraform_remote_state" "networking" {
  backend = "s3"
  config = {
    bucket  = "<YOUR_GENERATED_BUCKET_NAME>"
    key     = "cleanmybelly/infra/shared/networking/terraform.tfstate"
    region  = "us-east-1"
    profile = "terraform-user"
  }
}

module "frontend" {
  source = "../../../modules/frontend"

  environment  = "prod"
  project_name = var.project_name

  # Domain details (production uses the root domain)
  domain_name = data.terraform_remote_state.networking.outputs.hosted_zone_name

  # SSL/TLS Certificate fetched dynamically
  acm_certificate_arn = data.terraform_remote_state.networking.outputs.prod_frontend_cert_arn
}
