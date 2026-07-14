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

module "frontend" {
  source = "../../../modules/frontend"

  environment      = "prod"
  project_name     = var.project_name
  domain_name      = var.domain_name
  hosted_zone_name = var.hosted_zone_name

  # Injects certificates and backend variables
  acm_certificate_arn = var.acm_certificate_arn
}
