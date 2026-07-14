variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Name of the project"
  default     = "cleanmybelly"
}

variable "db_table_name" {
  type        = string
  description = "DynamoDB table name for prod backend"
  default     = "leads-coupons"
}

variable "db_hash_key" {
  type        = string
  description = "Primary partition key for DynamoDB table"
  default     = "phone_number"
}
