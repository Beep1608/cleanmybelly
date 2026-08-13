# Operations: Environment & Variables Synchronization (`env-sync`)

This operational guide provides step-by-step instructions for managing environment variables, generating local Terraform variable files (`.tfvars`), maintaining blueprints, and managing remote state backend configurations across all modules using **`tools/env_sync.py`**.

---

## 1. CLI Usage & Command Modes

The `env-sync` tool supports three operational modes:

### 1️⃣ Full Synchronization Mode (Default)
Scans all scopes, validates DSL syntax, autoverifies directory leaves, and updates/creates all `.env`, `.env.example`, `.tfvars`, `.example`, and `.tfbackend` files across all directions:
```bash
python3 tools/env_sync.py
```

### 2️⃣ Dry-Run Preview Mode (`--dry-run`)
Analyzes the workspace and prints a complete list of proposed file modifications without making any changes on disk:
```bash
python3 tools/env_sync.py --dry-run
```

### 3️⃣ CI/CD Validation Mode (`--validate`)
Validates that all `.env` and `.example` files are syntactically sound and that all Terraform modules are 100% in sync with their `.env` definitions. Returns exit code `0` on success and `1` on desynchronization:
```bash
python3 tools/env_sync.py --validate
```

---

## 2. First-Time Repository Onboarding Workflow

When cloning the repository for the first time, all root module `.tfvars` and `.tfbackend` files are omitted from source control. Follow this procedure to initialize your environment:

1. **Step 1: Copy Environment Templates**:
   Create the four local `.env` files from their committed `.example` blueprints:
   ```bash
   cp environments/global/.env.pre-infra.example  environments/global/.env.pre-infra
   cp environments/global/.env.shared.example     environments/global/.env.shared
   cp environments/dev/.env.dev.example           environments/dev/.env.dev
   cp environments/prod/.env.prod.example         environments/prod/.env.prod
   ```

2. **Step 2: Populate Secrets and Configuration Values**:
   Edit the `.env` files with your deployment parameters (e.g. `github_token`, `hosted_zone_name`, AWS region, project name).

3. **Step 3: Execute `env-sync`**:
   ```bash
   python3 tools/env_sync.py
   ```
   `env-sync` automatically creates:
   * `terraform.tfvars` (containing real local values)
   * `terraform.tfvars.example` (containing template definitions)
   * `backend.tfbackend` (containing S3 bucket config for all modules with remote state)
   * `backend.tfbackend.example` (containing empty backend templates)

---

## 3. Adding or Modifying Variables

`env-sync` supports full multi-directional propagation:

### Approach A: Declare in `.env` (Top-Down)
1. Open the corresponding `.env` file under `environments/`.
2. Add the variable under the desired module directive:
   ```ini
   [bootstrap | iam-deployer]
   my_new_parameter = "custom-value"
   ```
3. Run `python3 tools/env_sync.py`.
4. **Propagated automatically to**:
   * `.env.example`: Receives `my_new_parameter = ""` (Lateral Sync).
   * `variables.tf`: Automatically appends `variable "my_new_parameter" {}` (Forward Sync).
   * `terraform.tfvars`: Receives `my_new_parameter = "custom-value"`.
   * `terraform.tfvars.example`: Receives `my_new_parameter = ""`.

### Approach B: Declare in `variables.tf` (Bottom-Up)
1. Declare a new variable in any leaf module's `variables.tf`:
   ```hcl
   variable "discovered_setting" {
     type = string
   }
   ```
2. Run `python3 tools/env_sync.py`.
3. **Propagated automatically to**:
   * `.env`: Injected under `[module_name]` (Reverse Sync).
   * `.env.example`: Injected template under `[module_name]` (Lateral Sync).
   * `terraform.tfvars` and `terraform.tfvars.example`: Generated/updated in the module.

---

## 4. Modifying Backend State Bucket Configurations

When pointing your local modules to a newly created or existing S3 Remote State bucket:

1. In `environments/global/.env.pre-infra` (and other `.env` files), update the `!terraform_state_bucket` directive:
   ```ini
   [*]
   !terraform_state_bucket = "cleanmybelly-tfstate-v1-8b543648"
   ```
2. Execute `env-sync`:
   ```bash
   python3 tools/env_sync.py
   ```
3. Initialize or re-initialize Terraform modules with backend configuration:
   ```bash
   cd aws/pre-infra/iam-deployer
   terraform init -backend-config=backend.tfbackend -reconfigure
   ```

---

## 5. Troubleshooting & Common Error Diagnoses

### Missing `.env` Files Error
```text
❌ ERRORES DETECTADOS:
  ERROR: Los siguientes archivos .env no existen:
   → environments/global/.env.pre-infra
```
* **Cause**: `env-sync` requires all four `.env` files to be present before executing.
* **Resolution**: Run the `cp` command provided in the error output to create missing files from `.example` templates.

### `LexicalError`: Intermediate Directory Used as Target Token
```text
❌ Error Léxico en .env.pre-infra, línea 10:
  Token 'github' no es un módulo hoja válido.
  'github' contiene subdirectorios con módulos Terraform.
  Tokens válidos para esta ruta: github/oidc, github/repository, github/secrets-workflow
```
* **Cause**: Directives must target **leaf modules** directly. Target paths cannot stop at intermediate folders.
* **Resolution**: Replace `[github]` with specific leaves: `[github/oidc | github/repository | github/secrets-workflow]`.

### `SyntaxError`: Wildcard Combined with Module Token
```text
❌ Error Sintáctico en .env.pre-infra, línea 3:
  El wildcard '[*]' no se puede combinar con módulos específicos: '[* | bootstrap]'
```
* **Cause**: Wildcard `[*]` must be declared exclusively on its own line.
* **Resolution**: Separate into `[*]` on one line and `[bootstrap]` on a separate directive line.
