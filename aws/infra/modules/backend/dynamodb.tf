resource "aws_dynamodb_table" "data_table" {
  name         = "${var.project_name}-${var.environment}-${var.db_table_name}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = var.db_hash_key

  attribute {
    name = var.db_hash_key
    type = var.db_hash_key_type
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
