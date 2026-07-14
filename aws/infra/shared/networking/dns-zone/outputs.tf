output "hosted_zone_id" {
  description = "ID of the Route 53 Hosted Zone"
  value       = aws_route53_zone.primary.zone_id
}

output "hosted_zone_name" {
  description = "Name of the Route 53 Hosted Zone"
  value       = aws_route53_zone.primary.name
}

output "name_servers" {
  description = "Name Servers assigned to the Route 53 Hosted Zone. Update your domain registrar with these."
  value       = aws_route53_zone.primary.name_servers
}
