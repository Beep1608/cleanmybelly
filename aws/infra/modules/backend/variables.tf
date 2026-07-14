variable "project_name" {
  type        = string
  description = "Agnostic project or funnel code identifier"
}

variable "environment" {
  type        = string
  description = "Execution environment (e.g., dev, prod, staging)"
}

variable "db_table_name" {
  type        = string
  description = "Name of the main persistent database table"
  default     = "primary-data"
}

variable "db_hash_key" {
  type        = string
  description = "Partition key (Hash Key) for the DynamoDB table"
  default     = "id"
}

variable "db_hash_key_type" {
  type        = string
  description = "Data type of the partition key (S=String, N=Number, B=Binary)"
  default     = "S"
}

variable "lambda_handler" {
  type        = string
  description = "Entry point of the backend logic function"
  default     = "index.handler"
}

variable "lambda_runtime" {
  type        = string
  description = "Runtime environment for the serverless code"
  default     = "nodejs20.x"
}

variable "lambda_zip_path" {
  type        = string
  description = "Relative path to compiled zip package containing application code"
}
