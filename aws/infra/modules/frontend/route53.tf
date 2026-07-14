data "aws_route53_zone" "primary" {
  name         = var.hosted_zone_name
  private_zone = false
}

resource "aws_route53_record" "frontend_dns" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.cdn.domain_name
    zone_id                = aws_cloudfront_distribution.cdn.hosted_zone_id
    evaluate_target_health = false
  }
}
