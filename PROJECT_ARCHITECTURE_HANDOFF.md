# Project Architecture Handoff & Context Document

This document summarizes the core architectural vision, technical resolutions, design decisions, and active work-in-progress for the **cleanmybelly** project. It serves as a context bridge when continuing development in a new workspace or session.

---

## 1. Core Project Vision & Focus

* **Project Nature**: **cleanmybelly** is an **Open-Source Fullstack Serverless Cloud Boilerplate / Starter Kit**.
* **Primary Goal**: Allow any developer to clone the repository, run Phase 0 infrastructure bootstrapping with Terraform, and instantly have a production-grade, multi-environment (`dev` and `prod`) cloud infrastructure in AWS that **scales to 0** (costing $0.00 USD when idle).
* **Key Architecture Characteristics**:
  * **Serverless First**: AWS S3 + CloudFront CDN for Frontend (Next.js), HTTP API Gateway + AWS Lambda for Backend (Node.js), DynamoDB On-Demand for Database, Route 53 + ACM for DNS & SSL.
  * **Keyless Authentication**: Zero long-lived AWS Access Keys stored in GitHub. Uses AWS IAM OIDC Federation for GitHub Actions.
  * **AI-Assisted Harness & Skills**: Pre-configured agent workflows and architectural standards.

---

## 2. End-User Onboarding Lifecycle (3-Step Pattern)

```
 Step 1: Clone Starter Kit       Step 2: Terraform Phase 0               Step 3: Connect & Push
┌──────────────────────────┐    ┌──────────────────────────────────┐    ┌──────────────────────────────┐
│ git clone                │ ─► │ cd aws/pre-infra                 │ ─► │ git remote set-url origin... │
│ cleanmybelly.git         │    │ terraform apply                  │    │ git push origin main         │
│ mi-nuevo-proyecto        │    │ (Provisions user's GitHub Repo,  │    │ (Deploys automatically via   │
└──────────────────────────┘    │  AWS OIDC & Secrets Pipeline)    │    │  OIDC GitHub Actions to AWS) │
                                └──────────────────────────────────┘    └──────────────────────────────┘
```

1. **User Clones Boilerplate**: The user clones `cleanmybelly` to their local machine.
2. **User Runs Phase 0 (`aws/pre-infra/`)**:
   * Configures `github_org_or_username` and `github_repo_name` for their own GitHub account/organization.
   * `bootstrap`: Provisions S3 Remote State bucket in their AWS account.
   * `iam-deployer`: Provisions programmatic deployer IAM credentials for local CLI setup.
   * `github/repository`: Provisions the user's new repository on GitHub (with `auto_init = true`).
   * `github/oidc`: Establishes IAM OIDC Federated Trust between the user's GitHub repository and AWS.
   * `github/secrets-workflow`: Injects `AWS_ROLE_TO_ASSUME` secret and publishes the deployment pipeline `.github/workflows/deploy.yml`.
3. **User Develops & Pushes**: User develops in `app/frontend` and `app/backend`. Every push to `develop` or `main` automatically deploys to AWS via OIDC.

---

## 3. Key Technical Insights & Troubleshooting Solutions Learned

1. **GitHub PAT Permissions**:
   * Creating/Updating Repos requires `repo` scope (or `Administration: Read and Write` in Fine-Grained PAT).
   * Deleting Repositories via API (`DELETE /repos/...`) strictly requires the **`delete_repo`** scope in Classic PATs.
2. **Terraform State Locks**:
   * Interrupting `terraform plan`/`apply` with `Ctrl+C` leaves a lock on S3 state (`PreconditionFailed`).
   * **Resolution**: Use `terraform force-unlock <LOCK_ID>` after verifying no concurrent executions exist.
3. **State Management vs Real World (`terraform state rm`)**:
   * Removing a resource from state (`terraform state rm <address>`) untracks it from `.tfstate` without deleting the real resource on GitHub or AWS.
4. **Terraform Remote State Outputs (`data.terraform_remote_state`)**:
   * Outputs defined in `outputs.tf` are only written to the S3 `.tfstate` file after a **successful `terraform apply`**. Running `terraform plan` previews outputs (`+`), but does not write them to S3.
5. **GitHub API Empty Repo (`404 Not Found` on `github_repository_file`)**:
   * `github_repository_file` requires the target branch (e.g. `main`) to exist. An empty repo with `auto_init = false` has 0 commits and no branches.
   * `auto_init = true` only works during repo **creation** (`POST`), not on retroactive `PATCH` updates.
   * **Resolution**: Ensure initial commit/branch `main` exists before writing workflow files via Terraform.
6. **Perpetual Drift on `has_wiki`**:
   * GitHub Free private repositories do not support Wikis. Setting `has_wiki = true` on a private repo causes GitHub API to return `has_wiki = false`, creating a perpetual diff in `terraform plan`. Set `has_wiki = false` for private repos.

---

## 4. Architectural Agreements & Standards

### A. Environment Mapping & Git Branching Strategy
* **`develop` branch** ➔ Triggers CI/CD to deploy to AWS **`dev`** environment (`aws/infra/environments/dev/` ➔ `dev.domain.com`).
* **`main` branch** ➔ Triggers CI/CD to deploy to AWS **`prod`** environment (`aws/infra/environments/prod/` ➔ `domain.com`).

### B. Single Dynamic Workflow Strategy (`.github/workflows/deploy.yml`)
* To prevent Git merge conflicts when merging `develop` into `main`, **a single dynamic workflow file** is used.
* The workflow evaluates `${{ github.ref_name }}` dynamically:
  * If `develop` ➔ sets target environment to `dev` ➔ reads outputs from `aws/infra/environments/dev/frontend`.
  * If `main` ➔ sets target environment to `prod` ➔ reads outputs from `aws/infra/environments/prod/frontend`.

### C. Zero Structural Drift via Reusable Modules (`aws/infra/modules/`)
* Architecture logic is defined **once** inside reusable modules:
  * `aws/infra/modules/frontend/` (S3 + CloudFront CDN)
  * `aws/infra/modules/backend/` (API Gateway + Lambda + DynamoDB)
* Both `dev/` and `prod/` environment directories simply call these modules with environment-specific variables (`environment = "dev"` vs `environment = "prod"`). This guarantees 100% structural parity between environments.

### D. Layer Separation Responsibility
* **Base Infrastructure (`/aws`)**: Provisioned and updated via local Terraform CLI (`terraform apply`) by the administrator/developer.
* **Application Code (`/app`)**: Deployed continuously via automated GitHub Actions OIDC pipeline upon code pushes.

---

## 5. Next Steps & Active Action Items for New Session

1. **Verify Phase 0 Completion**:
   * Ensure `aws/pre-infra/github/repository`, `oidc`, and `secrets-workflow` are applied cleanly for the target repo.
2. **Implement Reusable Modules Structure**:
   * Refactor/verify `aws/infra/modules/frontend` and `aws/infra/modules/backend`.
   * Update `aws/infra/environments/dev/` and `aws/infra/environments/prod/` to consume `aws/infra/modules/*`.
3. **Deploy Core Environments**:
   * Execute Step 5 & Step 6 of `docs/getting_started.md`:
     * `aws/infra/environments/dev/backend`
     * `aws/infra/environments/dev/frontend`
4. **Deploy Application Pipeline**:
   * Verify dynamic `.github/workflows/deploy.yml` on `develop` and `main` branches.
