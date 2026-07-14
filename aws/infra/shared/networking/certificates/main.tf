data "aws_route53_zone" "primary" {
  name         = var.hosted_zone_name
  private_zone = false
}

# --- DEV CERTIFICATES ---

# Dev Frontend Certificate (CloudFront requires us-east-1)
resource "aws_acm_certificate" "dev_frontend" {
  provider          = aws.us_east_1
  domain_name       = "dev.${var.hosted_zone_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Dev Backend Certificate
resource "aws_acm_certificate" "dev_backend" {
  domain_name       = "api-dev.${var.hosted_zone_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# --- PROD CERTIFICATES ---

# Prod Frontend Certificate (CloudFront requires us-east-1)
resource "aws_acm_certificate" "prod_frontend" {
  provider          = aws.us_east_1
  domain_name       = var.hosted_zone_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Prod Backend Certificate
resource "aws_acm_certificate" "prod_backend" {
  domain_name       = "api.${var.hosted_zone_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# --- DNS VALIDATION RECORDS ---

# Dev Frontend validation record
resource "aws_route53_record" "dev_frontend_validation" {
  for_each = {
    for dvo in aws_acm_certificate.dev_frontend.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.primary.zone_id
}

# Dev Backend validation record
resource "aws_route53_record" "dev_backend_validation" {
  for_each = {
    for dvo in aws_acm_certificate.dev_backend.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.primary.zone_id
}

# Prod Frontend validation record
resource "aws_route53_record" "prod_frontend_validation" {
  for_each = {
    for dvo in aws_acm_certificate.prod_frontend.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.primary.zone_id
}

# Prod Backend validation record
resource "aws_route53_record" "prod_backend_validation" {
  for_each = {
    for dvo in aws_acm_certificate.prod_backend.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.primary.zone_id
}

# --- ACM VALIDATION TRIGGER ---

resource "aws_acm_certificate_validation" "dev_frontend" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.dev_frontend.arn
  validation_record_fqdns = [for record in aws_route53_record.dev_frontend_validation : record.fqdn]
}

resource "aws_acm_certificate_validation" "dev_backend" {
  certificate_arn         = aws_acm_certificate.dev_backend.arn
  validation_record_fqdns = [for record in aws_route53_record.dev_backend_validation : record.fqdn]
}

resource "aws_acm_certificate_validation" "prod_frontend" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.prod_frontend.arn
  validation_record_fqdns = [for record in aws_route53_record.prod_frontend_validation : record.fqdn]
}

resource "aws_acm_certificate_validation" "prod_backend" {
  certificate_arn         = aws_acm_certificate.prod_backend.arn
  validation_record_fqdns = [for record in aws_route53_record.prod_backend_validation : record.fqdn]
}
