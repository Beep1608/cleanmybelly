# cleanmybelly Automation Tools Ecosystem (`tools/`)

This directory houses automated Python CLI utilities designed for deterministic infrastructure bootstrapping, environment variable synchronization, and operational management across the **cleanmybelly** AWS ecosystem.

---

## Available Utilities

### 1. `tools/env_sync.py` — Environment & Variable Synchronizer
A deterministic CLI tool that synchronizes centralized environment variables (`environments/`) across all Terraform leaf modules in `aws/`:

* **Single Source of Truth**: Centralizes variables in `.env` files using section-targeting directives (`[modulo1 | modulo2]` and wildcard `[*]`).
* **Zero Dirty Diffs**: Implements Terraform Partial Backend Configuration (`backend.tfbackend` with `-backend-config`) to eliminate find & replace modifications on tracked `.tf` files.
* **Leaf Autodiscovery**: Scans `aws/` dynamically and indexes all 11 leaf modules while ignoring `.terraform/` and cache directories.
* **Usage**:
  ```bash
  python3 tools/env_sync.py            # Synchronize and generate all .tfvars and .tfbackend files
  python3 tools/env_sync.py --dry-run  # Preview proposed file changes without modifying disk
  python3 tools/env_sync.py --validate # CI/CD validation mode (exit 0 = in sync, exit 1 = desynced)
  ```
* **Detailed Documentation**:
  * Architecture: [`docs/architecture/env_sync.md`](../docs/architecture/env_sync.md)
  * Operations: [`docs/operations/env_sync.md`](../docs/operations/env_sync.md)
  * DSL Specification: [`docs/reference/env_sync_dsl.md`](../docs/reference/env_sync_dsl.md)

---

### 2. `tools/bootstrap.py` — End-to-End Bootstrap Orchestrator
An automated, interactive Python orchestrator that executes the complete Phase 0 setup and shared networking deployment on AWS & GitHub:

1. **Prerequisites Verification**: Validates Python, Terraform CLI, AWS CLI, and Git workspace.
2. **Interactive AWS Profile Selector**: Interactively selects active AWS CLI profile.
3. **Identity & Permission Validation**: Validates AWS credentials and tests administrative permissions.
4. **Interactive Configuration**: Prompts for required deployment variables (GitHub PAT, username, repo name, domain, AWS region).
5. **Phase 1: S3 State Bucket**: Provisions initial remote state bucket (`pre-infra/bootstrap`).
6. **Phase 2: Environment & Backend Sync**: Injects state bucket into `environments/global/.env.pre-infra` and calls `env-sync` programmatically.
7. **Phase 3: Deployer User**: Provisions `terraform-deployer` IAM user (`pre-infra/iam-deployer`).
8. **Phase 4: AWS CLI Profile**: Configures local AWS CLI profile `terraform-user`.
9. **Phase 5: GitHub Repository**: Provisions new GitHub repository (`pre-infra/github/repository`).
10. **Phase 6: Remote Origin Binding**: Connects local clone and pushes codebase to `main`.
11. **Phase 7: OIDC Federation**: Provisions AWS IAM OIDC Trust (`pre-infra/github/oidc`).
12. **Phase 8: Secrets & Workflow**: Injects `AWS_ROLE_TO_ASSUME` secret and publishes workflow (`pre-infra/github/secrets-workflow`).
13. **Phase 9: Route 53 DNS Zone**: Provisions primary hosted zone (`infra/shared/networking/dns-zone`).
14. **Phase 10: Registrar Setup Pause**: Pauses with interactive display of AWS Name Servers for custom DNS setup at registrar.
15. **Phase 11: ACM SSL Certificates**: Requests and validates SSL certificates (`infra/shared/networking/certificates`).

* **Usage**:
  ```bash
  python3 tools/bootstrap.py
  python3 tools/bootstrap.py --skip-permission-check
  ```
* **Detailed Documentation**:
  * Reference: [`docs/reference/bootstrap_cli.md`](../docs/reference/bootstrap_cli.md)
  * Operations: [`docs/operations/bootstrap.md`](../docs/operations/bootstrap.md)

---

## Modular Framework Architecture

```text
tools/
├── README.md                           # This document
├── bootstrap.py                        # Bootstrap entrypoint CLI
├── env_sync.py                         # env-sync entrypoint CLI
├── shared/                             # Core framework shared across tools
│   ├── outputs/                        # ExecutionTracker & OutputManager
│   ├── ui/                             # ANSI color logger & box formatters
│   └── utils/                          # Subprocess runner & repo root finder
└── modules/                            # Modular implementations
    ├── bootstrap/                      # Encapsulated bootstrap domain logic
    └── env_sync/                       # Encapsulated env-sync engine (scope_map, lexer, parser, synchronizer)
```
