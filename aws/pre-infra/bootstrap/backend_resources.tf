# Generate a random suffix to ensure global uniqueness for the S3 bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 Bucket for Terraform Remote State and Native State Locking
# Enforces lowercase naming convention: ${var.project_name}-tfstate-${var.project_version}-[random]
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${lower(var.project_name)}-tfstate-${var.project_version}-${random_id.bucket_suffix.hex}"

  tags = {
    Project     = var.project_name
    Version     = var.project_version
    Description = "Terraform remote state storage and native state locking"
    ManagedBy   = "Terraform pre-infra"
  }
}

# Enable versioning to allow state recovery in case of accidental corruption
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enforce server-side encryption by default (SSE-S3)
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_crypto" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access to the state bucket to prevent data leaks
resource "aws_s3_bucket_public_access_block" "terraform_state_access" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}