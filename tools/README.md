# cleanmybelly Bootstrap CLI Tool (`tools/bootstrap.py`)

The **Bootstrap CLI Tool** is an automated, console-based Python utility designed to execute the complete end-to-end infrastructure bootstrapping process for the **cleanmybelly** project on AWS and GitHub.

---

## Overview

Instead of manually navigating through multiple Terraform directories and running commands step-by-step, `tools/bootstrap.py` automates the entire Phase 0 setup in a single, interactive execution:

1. **Prerequisites Verification**: Validates Python, Terraform CLI, AWS CLI, active AWS identity, AWS permissions, and Git workspace.
2. **Interactive Configuration**: Prompts for required deployment variables (GitHub PAT, username, repo name, domain, AWS region).
3. **Phase 1: S3 State Bucket**: Provisions the initial remote state bucket (`pre-infra/bootstrap`).
4. **Phase 2: Global Config Update**: Performs automatic Find & Replace across all `providers.tf` files with the generated bucket name.
5. **Phase 3: Deployer User**: Provisions the `terraform-deployer` IAM user and credentials (`pre-infra/iam-deployer`).
6. **Phase 4: AWS CLI Profile**: Configures the local AWS CLI profile `terraform-user`.
7. **Phase 5: GitHub Repository**: Provisions the new GitHub repository (`pre-infra/github/repository`).
8. **Phase 6: Remote Origin Binding**: Connects local clone to the new GitHub repository (`git remote set-url origin`) and pushes the codebase to `main`.
9. **Phase 7: OIDC Federation**: Provisions the AWS IAM OIDC Trust (`pre-infra/github/oidc`).
10. **Phase 8: Secrets & Workflow**: Injects `AWS_ROLE_TO_ASSUME` secret and publishes `.github/workflows/deploy-frontend.yml` (`pre-infra/github/secrets-workflow`).
11. **Phase 9: Route 53 DNS Zone**: Provisions the primary hosted zone (`infra/shared/networking/dns-zone`).
12. **Phase 10: Registrar Setup Pause**: Pauses with interactive display of AWS Name Servers for custom DNS setup at registrar (e.g. Namecheap) and verifies propagation.
13. **Phase 11: ACM SSL Certificates**: Requests and validates SSL certificates (`infra/shared/networking/certificates`).

---

## Prerequisites

Before running the tool, ensure:
* **Python**: `>= 3.8`
* **Terraform CLI**: `>= 1.10.0`
* **AWS CLI**: `v2` configured with administrative access for initial bootstrapping
* **Git**: `>= 2.0`
* **GitHub Personal Access Token (PAT)**: Classic token with `repo` and `workflow` scopes (or Fine-Grained token with `Administration`, `Contents`, `Secrets`, and `Workflows` read/write access).

---

## Usage

Run the tool from the repository root:

```bash
python3 tools/bootstrap.py
```

---

## Output File (`tools/bootstrap_outputs.json`)

Upon successful execution, important outputs and resource identifiers are saved to `tools/bootstrap_outputs.json`:

```json
{
  "timestamp": "2026-08-10T12:00:00Z",
  "terraform_state_bucket": "cleanmybelly-tfstate-v1-8b543648",
  "iam_deployer_user": "terraform-deployer",
  "iam_deployer_access_key_id": "AKIA...",
  "iam_deployer_secret_access_key": "[CONFIGURED IN AWS PROFILE 'terraform-user']",
  "github_repository_url": "https://github.com/JoseLopezLara/cleanmybelly",
  "github_repository_full_name": "JoseLopezLara/cleanmybelly",
  "github_actions_role_arn": "arn:aws:iam::123456789012:role/github-actions-deployer-role",
  "route53_zone_id": "Z0123456789ABCDEF",
  "route53_name_servers": [
    "ns-1234.awsdns-12.org",
    "ns-5678.awsdns-34.co.uk",
    "ns-9012.awsdns-56.com",
    "ns-3456.awsdns-78.net"
  ],
  "acm_certificates": {
    "dev_frontend_cert_arn": "arn:aws:acm:us-east-1:123456789012:certificate/...",
    "dev_backend_cert_arn": "arn:aws:acm:us-east-1:123456789012:certificate/...",
    "prod_frontend_cert_arn": "arn:aws:acm:us-east-1:123456789012:certificate/...",
    "prod_backend_cert_arn": "arn:aws:acm:us-east-1:123456789012:certificate/..."
  }
}
```

> ⚠️ **Note**: `tools/bootstrap_outputs.json` is automatically ignored in `.gitignore` to prevent committing generated state details.
