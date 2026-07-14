output "api_gateway_url" {
  description = "Agnostic entrypoint endpoint for client HTTP requests"
  value       = aws_apigatewayv2_stage.api_stage.invoke_url
}
