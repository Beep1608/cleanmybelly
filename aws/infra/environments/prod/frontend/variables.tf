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

variable "terraform_state_bucket_name" {
  type        = string
  description = "Name of the S3 bucket storing Terraform remote state"
}
