output "api_gateway_url" {
  description = "Raw invoke URL of the API Gateway HTTP API"
  value       = aws_apigatewayv2_stage.api_stage.invoke_url
}

output "custom_domain_url" {
  description = "Custom domain URL for the API Gateway endpoint"
  value       = "https://${var.domain_name}"
}

output "apigateway_target_domain_name" {
  description = "Target domain name for API Gateway custom domain (for DNS route mapping)"
  value       = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].target_domain_name
}

output "apigateway_hosted_zone_id" {
  description = "Hosted Zone ID for the custom domain endpoint"
  value       = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].hosted_zone_id
}
