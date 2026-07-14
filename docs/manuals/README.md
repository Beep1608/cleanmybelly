# Infrastructure and Operations Manuals

This directory contains technical manuals and step-by-step guides for managing the cleanmybelly platform infrastructure, domain routing, and CI/CD automation pipelines.

---

## Manuals Directory Index

| Manual | Description | Topic | File Path |
| :--- | :--- | :--- | :--- |
| **Domain Delegation Guide** | Instructions for delegating custom domains from Namecheap to AWS Route 53 using Nameservers. | DNS Routing | [README.md](dns/README.md) |
| **Monorepo Frontend Pipeline Guide** | GitHub Actions workflow configuration for path-based deployment of the frontend application to S3 and CloudFront. | CI/CD Automation | [github_actions_monorepo.md](pipelines/github_actions_monorepo.md) |

---

## Navigation and Usage

1. Select a guide from the table above based on your operational requirement.
2. Ensure you have completed the bootstrap pre-infrastructure setup before attempting environment deployments or domain configuration.
3. For infrastructure codebase blueprints and service layouts, refer to the root infrastructure documentation.
