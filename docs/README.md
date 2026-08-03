# Cloud Infrastructure Documentation Hub

Welcome to the **cleanmybelly** cloud infrastructure documentation hub. This repository contains detailed technical documentation, operational manuals, architecture blueprints, and agent skills specifications for our AWS serverless ecosystem.

---

## 🚀 Quick Start for New Developers

If you are new to the project or deploying the infrastructure from zero, start directly with the linear step-by-step onboarding guide:

👉 **[Getting Started: Complete Infrastructure Deployment Guide](getting_started.md)**

---

## 🗺️ Documentation Master Navigation Map

```mermaid
graph TD
    Start[Project Documentation Hub] --> GS["1. Linear Onboarding Walkthrough (getting_started.md)"]
    Start --> Arch
    Start --> Ops
    Start --> Ref

    subgraph Arch [2. Architecture & Concepts]
        direction TB
        Arch_Back["Backend Architecture (architecture/backend.md)"]
        Arch_Front["Frontend Architecture (architecture/frontend.md)"]
        Arch_AWS["AWS Services Catalog (architecture/aws_services.md)"]
        Arch_Back --> Arch_Front --> Arch_AWS
    end

    subgraph Ops [3. Operational How-To Guides]
        direction TB
        Ops_PAT["GitHub PAT Setup (operations/github_pat_setup.md)"]
        Ops_Boot["Phase 0 Bootstrap & OIDC (operations/bootstrap.md)"]
        Ops_DNS["Domain Delegation Guide (operations/dns_delegation.md)"]
        Ops_Sec["Secrets Management SSM (operations/secrets_management.md)"]
        Ops_CDN["Manual CDN Invalidation (operations/cdn_invalidation.md)"]
        Ops_OIDC["OIDC Audit Reference (operations/github_oidc_verification.md)"]
        Ops_PAT --> Ops_Boot --> Ops_DNS --> Ops_Sec --> Ops_CDN --> Ops_OIDC
    end

    subgraph Ref [4. Reference & Specs]
        direction TB
        Ref_Plan["Infrastructure Standards (reference/infrastructure_standards.md)"]
        Ref_Pipe["Monorepo Spec (reference/github_actions_monorepo.md)"]
        Ref_Skills["Agent Skills Catalog (reference/agent_skills.md)"]
        Ref_Plan --> Ref_Pipe --> Ref_Skills
    end
```

---

## 📚 Document Catalog Index

### 1. Architectural Explanations (`architecture/`)
Conceptual documentation explaining how system components interact under the hood:
* **[Backend Architecture](architecture/backend.md)**: Serverless compute flow, API Gateway routing, Lambda handlers, and DynamoDB data persistence.
* **[Frontend Architecture](architecture/frontend.md)**: Static content distribution using Client-Side Rendering (CSR), CloudFront CDN edge caching, and private S3 buckets.
* **[AWS Services Catalog](architecture/aws_services.md)**: Detailed catalog of the 11 AWS services powering the project.

### 2. Operational Procedures (`operations/`)
Actionable, step-by-step how-to guides for specific administrative and operational tasks:
* **[GitHub PAT Setup](operations/github_pat_setup.md)**: Instructions for generating and scoping a GitHub Personal Access Token for Terraform Phase 0 bootstrapping.
* **[Bootstrap & Federation Setup](operations/bootstrap.md)**: Phase 0 setup of S3 remote state buckets, deployer credentials, and GitHub OIDC trust via Terraform.
* **[Domain Delegation Guide](operations/dns_delegation.md)**: Procedure for delegating domain name servers from Namecheap to AWS Route 53.
* **[Application Secrets Management](operations/secrets_management.md)**: Instructions for adding and rotating encrypted SSM Parameter Store secrets via CLI and Web Console.
* **[Static Asset Sync & CDN Invalidation](operations/cdn_invalidation.md)**: CLI commands to manually sync compiled Next.js assets to S3 and flush CloudFront edge cache.
* **[GitHub OIDC Verification](operations/github_oidc_verification.md)**: Policy reference for auditing IAM role permissions and trust relationships.

### 3. Technical References (`reference/`)
Specifications, directory layouts, and configuration blueprints:
* **[Infrastructure Directory & State Standards](reference/infrastructure_standards.md)**: Module directory layout, environment isolation strategy, S3 remote state key naming hierarchy, and cross-state HCL references.
* **[Monorepo CI/CD Pipeline Specification](reference/github_actions_monorepo.md)**: Path-triggered GitHub Actions workflow blueprint (`deploy-frontend.yml`).
* **[Agent Skills Catalog & Auto-Doc Standard](reference/agent_skills.md)**: Specifications, triggers, and catalog of repository agent skills (`docs-auditor`, `docs-writer`).

---

## ℹ️ Important Architecture Note (Terraform State Isolation)

> **State Isolation Strategy of Bootstrap Modules (`aws/pre-infra`):**
> 1. Only `aws/pre-infra/bootstrap` runs with **local state**, as its sole purpose is creating the S3 Remote State bucket (`cleanmybelly-tfstate-v1-*`).
> 2. All subsequent modules (`aws/pre-infra/iam-deployer`, `aws/pre-infra/github/*`, and `/aws/infra/...`) store their `.tfstate` files securely inside the **S3 Remote State bucket**.
> 3. This architecture guarantees complete traceability and allows updating deployer IAM policies or GitHub integration settings from any machine at any time.
> 4. Right after Step 1 bootstrap, developers perform a workspace-wide Find & Replace (`Ctrl+F`) replacing `<TERRAFORM_STATE_BUCKET_NAME>` (and legacy placeholders `<YOUR_TFSTATE_BUCKET_NAME>` or `<YOUR_GENERATED_BUCKET_NAME>`) with the generated S3 bucket name in all `providers.tf` files.
