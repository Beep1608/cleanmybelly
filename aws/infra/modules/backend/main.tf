# Place your core backend serverless infrastructure resources here
# (Lambda, API Gateway, DynamoDB, IAM roles, and CloudWatch Logs configuration)

variable "environment" {
  type        = string
  description = "Environment identifier (e.g. dev, prod)"
}
