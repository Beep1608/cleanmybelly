# IAM Role for Serverless Execution
resource "aws_iam_role" "lambda_exec" {
  name = "${var.project_name}-${var.environment}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach Standard CloudWatch Writing Permission
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Grant Read/Write access only to the parameterized DynamoDB Table
resource "aws_iam_role_policy" "lambda_database_access" {
  name = "${var.project_name}-${var.environment}-lambda-db-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ]
      Resource = aws_dynamodb_table.data_table.arn
    }]
  })
}

# Standard Serverless Compute Node
resource "aws_lambda_function" "api_handler" {
  function_name = "${var.project_name}-${var.environment}-api-handler"
  role          = aws_iam_role.lambda_exec.arn
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  filename      = var.lambda_zip_path

  # Source hash is checked to automatically redeploy on code updates
  source_code_hash = fileexists(var.lambda_zip_path) ? filebase64sha256(var.lambda_zip_path) : null

  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.data_table.name
      ENVIRONMENT = var.environment
      PROJECT     = var.project_name
    }
  }
}
