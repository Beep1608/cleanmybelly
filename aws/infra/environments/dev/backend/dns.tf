# DNS mapping for Dev API Gateway custom domain
resource "aws_route53_record" "api_dns" {
  zone_id = data.terraform_remote_state.networking.outputs.hosted_zone_id
  name    = "api-dev.${data.terraform_remote_state.networking.outputs.hosted_zone_name}"
  type    = "A"

  alias {
    name                   = module.backend.apigateway_target_domain_name
    zone_id                = module.backend.apigateway_hosted_zone_id
    evaluate_target_health = false
  }
}
