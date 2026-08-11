# Read Shared Networking outputs (Route 53 hosted zone and SSL certificates)
data "terraform_remote_state" "networking" {
  backend = "s3"
  config = {
    bucket  = "<TERRAFORM_STATE_BUCKET_NAME>"
    key     = "cleanmybelly/infra/shared/networking/terraform.tfstate"
    region  = "us-east-1"
    profile = "terraform-user"
  }
}

# Archive data source to build placeholder.zip dynamically from index.py
data "archive_file" "backend_lambda" {
  type        = "zip"
  source_file = "${path.module}/index.py"
  output_path = "${path.module}/placeholder.zip"
}

module "backend" {
  source = "../../../modules/backend"

  environment  = "dev"
  project_name = var.project_name

  # Database details
  db_table_name = var.db_table_name
  db_hash_key   = var.db_hash_key
  enable_pitr   = false # Disabled in dev to optimize and keep costs at absolute zero

  # API Domain Mapping
  domain_name         = "api-dev.${data.terraform_remote_state.networking.outputs.hosted_zone_name}"
  acm_certificate_arn = data.terraform_remote_state.networking.outputs.dev_backend_cert_arn

  # CORS configuration (Only allows your Dev Frontend)
  cors_allow_origins = ["https://dev.${data.terraform_remote_state.networking.outputs.hosted_zone_name}"]

  # Lambda deployment zip package path
  lambda_zip_path = data.archive_file.backend_lambda.output_path

  # Lambda runtime and handler override for Python dummy function
  lambda_runtime = "python3.11"
  lambda_handler = "index.handler"
}
