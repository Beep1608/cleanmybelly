# DNS mapping for Prod Frontend domain pointing to CloudFront CDN
resource "aws_route53_record" "frontend_dns" {
  zone_id = data.terraform_remote_state.networking.outputs.hosted_zone_id
  name    = data.terraform_remote_state.networking.outputs.hosted_zone_name
  type    = "A"

  alias {
    name                   = module.frontend.cloudfront_domain_name
    zone_id                = module.frontend.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}
