module "backend" {
  source = "../../../modules/backend"

  environment  = "dev"
  project_name = var.project_name

  # Generic table naming parameters
  db_table_name = var.db_table_name
  db_hash_key   = var.db_hash_key

  # Configures the path where your deployment package is generated
  lambda_zip_path = "${path.module}/placeholder.zip" 
}
