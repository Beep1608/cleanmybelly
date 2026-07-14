# ACM Certificate configuration note:
# Since CloudFront requires SSL certificates to reside in the us-east-1 region,
# certificates are provisioned at the environment level and their ARNs are passed
# into this module via the `acm_certificate_arn` variable.
#
# This avoids pinning region providers inside reusable modules.
