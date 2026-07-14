output "raw_api_gateway_url" {
  description = "Raw API Gateway execute URL"
  value       = module.backend.api_gateway_url
}

output "custom_domain_url" {
  description = "Custom API domain endpoint"
  value       = module.backend.custom_domain_url
}
