# Initial Request: Terraform Remote Backend State, Partial Configuration & DSL Engine

## User Requirements Summary

The user requested a specialized architectural compression focused on:
1. **Terraform Remote Backend State Behavior**: Understanding how remote state configuration is decoupled from static infrastructure code using Terraform Partial Backend Configuration (`-backend-config=backend.tfbackend`).
2. **Selective Generation (Why only remote backend modules receive `backend.tfbackend`)**: Explaining why `aws/pre-infra/bootstrap` uses local state (because it provisions the remote bucket itself) and how `env-sync` excludes it dynamically.
3. **The `!` Prefix Mechanics in DSL**: Explaining how the `!` prefix separates backend configuration parameters from standard Terraform input variables.
4. **Attribute Name Translation (`!terraform_state_bucket` vs `bucket`)**: Explaining why the parameter is declared descriptively in `.env` as `!terraform_state_bucket` but must be translated strictly to `bucket = "..."` in `backend.tfbackend` due to HashiCorp Terraform S3 backend provider specifications.

---

## Technical Constraints & Design Principles

* **Zero Dirty Diffs**: Tracked `.tf` files (such as `providers.tf`) must never be mutated with dynamic bucket names during bootstrap or environment setup.
* **Deterministic Autodiscovery**: Leaf Terraform modules in `aws/` must be discovered dynamically without hardcoded path lists.
* **Single Source of Truth**: Centralized `.env` files in `environments/` define all deployment and backend variables.
* **Multi-Directional Synchronization**: Changes propagate bidirectionally between modules and `.env`, and laterally between `.env` and `.env.example`.
