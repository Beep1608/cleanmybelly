# Reference: Automated Bootstrap CLI Tool (`tools/bootstrap.py`)

This reference document specifies the design, capabilities, interactive prompt interface, execution phases, and output format of the automated Python Bootstrap CLI tool (`tools/bootstrap.py`).

---

## 1. Overview & Purpose

The **cleanmybelly Bootstrap CLI tool** automates the entire Phase 0 infrastructure setup and shared networking deployment in a single, interactive execution. 

Instead of manually navigating through multiple Terraform directories and running commands step-by-step, developers can run `python3 tools/bootstrap.py` to provision remote state storage, IAM credentials, GitHub repository integration, AWS OIDC federation, Route 53 DNS hosted zones, and ACM SSL certificates.

---

## 2. Execution Prerequisites

Before executing `python3 tools/bootstrap.py`, the CLI tool verifies the following system requirements:

| Prerequisite | Minimum Version / Requirement | Verification Method |
| :--- | :--- | :--- |
| **Python** | `>= 3.8` | `sys.version_info` |
| **Terraform CLI** | `>= 1.10.0` | `terraform version` |
| **AWS CLI** | `v2` | `aws --version` |
| **AWS Identity** | Active AWS CLI credentials | `aws sts get-caller-identity` |
| **AWS Permissions** | Administrative access for initial bootstrapping | IAM caller identity check & warning |
| **Git** | `>= 2.0` | `git rev-parse --is-inside-work-tree` |

---

## 3. Interactive Prompt Reference

At startup, the CLI tool prompts for configuration variables:

| Prompt | Description | Default Value | Validation Rule |
| :--- | :--- | :--- | :--- |
| **GitHub PAT** | Personal Access Token with `repo` and `workflow` scopes | None (Required) | Non-empty string |
| **GitHub Owner** | Username or organization name | `git config user.name` | Non-empty string |
| **Repository Name** | Name for the new GitHub repository | Directory name | Valid GitHub repo name |
| **Visibility** | Repository visibility (`public` or `private`) | `public` | Must be `public` or `private` |
| **Root Domain** | Domain name for Route 53 & ACM (e.g., `example.com`) | None (Required) | Valid domain format with `.` |
| **AWS Region** | AWS region for infrastructure deployment | `us-east-1` | Valid AWS region string |

---

## 4. Sequential Execution Phases

```mermaid
graph TD
    P0["Phase 0: Prerequisites Check"] --> P1["Phase 1: Bootstrap S3 State Bucket<br><i>(aws/pre-infra/bootstrap)</i>"]
    P1 --> P2["Phase 2: Global Find & Replace<br><i>(bucket name in providers.tf)</i>"]
    P2 --> P3["Phase 3: Deploy IAM Deployer User<br><i>(aws/pre-infra/iam-deployer)</i>"]
    P3 --> P4["Phase 4: Configure AWS CLI Profile<br><i>(terraform-user)</i>"]
    P4 --> P5["Phase 5: Provision GitHub Repository<br><i>(aws/pre-infra/github/repository)</i>"]
    P5 --> P6["Phase 6: Connect Local Clone<br><i>(git remote set-url & push)</i>"]
    P6 --> P7["Phase 7: Deploy OIDC Federation<br><i>(aws/pre-infra/github/oidc)</i>"]
    P7 --> P8["Phase 8: Secrets & Workflow Publishing<br><i>(aws/pre-infra/github/secrets-workflow)</i>"]
    P8 --> P9["Phase 9: Route 53 DNS Zone<br><i>(aws/infra/shared/networking/dns-zone)</i>"]
    P9 --> PAUSE["Phase 10: Manual Pause & Registrar Setup<br><i>(Configure Name Servers)</i>"]
    PAUSE --> P11["Phase 11: ACM SSL Certificates<br><i>(aws/infra/shared/networking/certificates)</i>"]
    P11 --> DONE["Output Report Saved<br><i>(tools/bootstrap_outputs.json)</i>"]
```

### Phase Descriptions

1. **Phase 1 (S3 State Bucket)**: Runs `terraform apply` in `aws/pre-infra/bootstrap` to create the initial S3 Remote State bucket (`cleanmybelly-tfstate-v1-*`).
2. **Phase 2 (Global Find & Replace)**: Replaces `<TERRAFORM_STATE_BUCKET_NAME>` and legacy placeholders in all `providers.tf` files workspace-wide with the generated bucket name.
3. **Phase 3 (IAM Deployer User)**: Runs `terraform apply` in `aws/pre-infra/iam-deployer` to create the `terraform-deployer` user and access keys.
4. **Phase 4 (AWS Profile Setup)**: Configures local AWS CLI profile `terraform-user` with the generated deployer access keys.
5. **Phase 5 (GitHub Repository)**: Runs `terraform apply` in `aws/pre-infra/github/repository` to provision the new GitHub repository.
6. **Phase 6 (Connect Local Clone)**: Configures `origin` remote URL non-interactively using owner and PAT credentials (`https://<owner>:<PAT>@github.com/<owner>/<repo>.git`) to eliminate password prompts. Pushes codebase to `main` branch, automatically handling auto-initialized repositories via `git pull origin main --rebase --allow-unrelated-histories` and force-push fallbacks.
7. **Phase 7 (OIDC Federation)**: Runs `terraform apply` in `aws/pre-infra/github/oidc` to establish IAM OIDC trust.
8. **Phase 8 (Secrets & Workflow)**: Runs `terraform apply` in `aws/pre-infra/github/secrets-workflow` to store `AWS_ROLE_TO_ASSUME` secret and publish `.github/workflows/deploy-frontend.yml`.
9. **Phase 9 (Route 53 DNS Zone)**: Runs `terraform apply` in `aws/infra/shared/networking/dns-zone` using the `terraform-user` profile.
10. **Phase 10 (Manual Registrar Setup & Pause)**: Displays the 4 AWS Name Servers generated by Route 53 in a formatted terminal box. Pauses execution until the developer updates their registrar (e.g. Namecheap) to Custom DNS and presses Enter. Verifies DNS propagation via `dig`.
11. **Phase 11 (ACM SSL Certificates)**: Runs `terraform apply` in `aws/infra/shared/networking/certificates` to request and validate SSL certificates.

---

## 5. Incremental Output Report & Execution Tracking

During execution, outputs and status metrics are updated **incrementally after each phase** across three dedicated files in `tools/`:

### A. Incremental Output Report (`tools/bootstrap_outputs.json`)
Updated dynamically upon completion of each phase to persist infrastructure outputs (e.g. state bucket, IAM deployer, repo URL, zone ID, certificates):

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
    "dev_backend_cert_arn": "arn:aws:acm:us-east-1:123456789012:certificate/..."
  }
}
```

### B. Dynamic Execution Status Tracker (`tools/bootstrap_status.json`)
Maintains the exact execution order, target directory, timestamp, status (`PENDING`, `IN_PROGRESS`, `SUCCESS`, `FAILED`), and error details for each phase step:

```json
{
  "start_time": "2026-08-10T12:00:00Z",
  "last_updated": "2026-08-10T12:05:00Z",
  "overall_status": "IN_PROGRESS",
  "current_phase": 5,
  "phases": [
    {
      "phase_number": 1,
      "name": "Bootstrap S3 Remote State Bucket",
      "target_dir": "aws/pre-infra/bootstrap",
      "status": "SUCCESS",
      "start_time": "2026-08-10T12:00:01Z",
      "end_time": "2026-08-10T12:00:15Z",
      "error_message": null
    }
  ]
}
```

### C. Live Execution Audit Log (`tools/bootstrap_status.log`)
Appends timestamped log lines for each phase lifecycle event for easy terminal tailing and debugging if an apply step fails.

> ⚠️ **Security Note**: `tools/bootstrap_outputs.json`, `tools/bootstrap_status.json`, and `tools/bootstrap_status.log` are listed in `.gitignore` to prevent committing generated state details to source control.
