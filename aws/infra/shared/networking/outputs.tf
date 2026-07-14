output "hosted_zone_id" {
  description = "ID of the Route 53 Hosted Zone"
  value       = aws_route53_zone.primary.zone_id
}

output "hosted_zone_name" {
  description = "Name of the Route 53 Hosted Zone"
  value       = aws_route53_zone.primary.name
}

output "dev_frontend_cert_arn" {
  description = "ACM certificate ARN for dev frontend (in us-east-1)"
  value       = aws_acm_certificate.dev_frontend.arn
}

output "dev_backend_cert_arn" {
  description = "ACM certificate ARN for dev backend"
  value       = aws_acm_certificate.dev_backend.arn
}

output "prod_frontend_cert_arn" {
  description = "ACM certificate ARN for prod frontend (in us-east-1)"
  value       = aws_acm_certificate.prod_frontend.arn
}

output "prod_backend_cert_arn" {
  description = "ACM certificate ARN for prod backend"
  value       = aws_acm_certificate.prod_backend.arn
}
