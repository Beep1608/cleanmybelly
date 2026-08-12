# Context Export: cleanmybelly Infrastructure & Documentation Refactoring

**Fecha de Exportación:** 2026-08-12  
**Repositorio:** `cleanmybelly` (`/home/jose-lopez-lara/Git/cleanmybelly`)  
**Propósito:** Transferencia completa del contexto de la conversación a una nueva ventana de chat / computadora.

---

## 1. Resumen de la Sesión y Estado Actual

En esta sesión realizamos dos grandes actividades:

1. **Auditoría Completa de Documentación (`docs/`):**
   - Se analizaron los 15 archivos de documentación bajo las reglas del skill `docs-auditor` y `documentation_standards.md`.
   - Se verificaron los 8 checks de cumplimiento (Taxonomía SRP, Inglés técnico, Política de Emojis, Precisión de nombres, Indexación en `docs/README.md`, Enlaces relativos, Diagramas Mermaid y Rutas absolutas del host).
   - **Resultado:** La documentación está 100% saludable y conforme a los estándares del proyecto.

2. **Diagnóstico y Plan de Refactorización de Infraestructura Terraform (`aws/` y `tools/`):**
   - Se diagnosticaron los 13 módulos de Terraform en `aws/pre-infra` y `aws/infra`.
   - Se detectó que 10 de 11 root modules carecen de `terraform.tfvars.example`.
   - Se detectaron valores personales hardcodeados en `github/repository/variables.tf` y `github/secrets-workflow/variables.tf` (`"JoseLopezLara"`, `"Test2"`).
   - Se detectó que `aws/pre-infra/bootstrap/main.tf` incluye los bloques `terraform {}` y `provider {}`, los cuales deben separarse a un nuevo `providers.tf`.
   - Se analizó el problema de la Fase 2 del bootstrap (`phase_02_find_replace.py`), que realiza find & replace en archivos `.tf` en Git generando diffs sucios.
   - Se concluyó técnicamente que Terraform **no permite variables en el bloque `backend {}`**, por lo que la mejor solución aprobada es **Partial Backend Configuration** con archivos `.tfbackend` ignorados en Git.
   - Se diseñó la nueva herramienta `tools/env_sync.py` y la estructura del directorio de entornos `environments/` en la raíz.
   - Se discutieron las alternativas de mapeo (Modelo Híbrido: `mapping.py` declarativo para propagación "uno a muchos" de variables compartidas + auto-descubrimiento para variables únicas/nuevas).

---

## 2. Diagnóstico Técnico de los Módulos Terraform

| Módulo | Ruta | `providers.tf` | `tfvars.example` | Estado / Acciones Requeridas |
| :--- | :--- | :---: | :---: | :--- |
| **Bootstrap** | `aws/pre-infra/bootstrap` | ❌ *(en `main.tf`)* | ✅ | Crear `providers.tf`, mover bloques `terraform{}` + `provider{}`. Limpiar defaults en `variables.tf`. |
| **IAM Deployer** | `aws/pre-infra/iam-deployer` | ✅ | ❌ | Eliminar `<TERRAFORM_STATE_BUCKET_NAME>` de `providers.tf`. Crear `terraform.tfvars.example`. |
| **GitHub Repo** | `aws/pre-infra/github/repository` | ✅ | ❌ | Eliminar placeholder en `providers.tf`. Limpiar hardcodes `"JoseLopezLara"`, `"Test2"`. Crear `.example`. |
| **GitHub OIDC** | `aws/pre-infra/github/oidc` | ✅ | ❌ | Eliminar placeholder en `providers.tf`. Crear `terraform.tfvars.example`. |
| **GitHub Secrets**| `aws/pre-infra/github/secrets-workflow`| ✅ | ❌ | Eliminar placeholder en `providers.tf`. Limpiar hardcode `"JoseLopezLara"`. Crear `.example`. |
| **DNS Zone** | `aws/infra/shared/networking/dns-zone` | ✅ | ❌ | Eliminar placeholder en `providers.tf`. Crear `terraform.tfvars.example`. |
| **Certificates** | `aws/infra/shared/networking/certificates` | ✅ | ❌ | Eliminar placeholder en `providers.tf`. Crear `terraform.tfvars.example`. |
| **Dev Backend** | `aws/infra/environments/dev/backend` | ✅ | ❌ | Eliminar placeholder en `providers.tf` y `main.tf`. Crear `terraform.tfvars.example`. |
| **Dev Frontend** | `aws/infra/environments/dev/frontend` | ✅ | ❌ | Eliminar placeholder en `providers.tf` y `main.tf`. Crear `terraform.tfvars.example`. |
| **Prod Backend** | `aws/infra/environments/prod/backend` | ✅ | ❌ | Eliminar placeholder en `providers.tf` y `main.tf`. Crear `terraform.tfvars.example`. |
| **Prod Frontend** | `aws/infra/environments/prod/frontend` | ✅ | ❌ | Eliminar placeholder en `providers.tf` y `main.tf`. Crear `terraform.tfvars.example`. |
| **Module Backend**| `aws/infra/modules/backend` | ❌ *(correcto)* | ❌ | Child module (hereda provider del root). Correcto por diseño. |
| **Module Frontend**| `aws/infra/modules/frontend` | ❌ *(correcto)* | ❌ | Child module (hereda provider del root). Correcto por diseño. |

---

## 3. Decisiones Técnicas Acordadas con el Usuario

1. **Partial Backend Configuration (Aprobado):**
   - Los archivos `providers.tf` tendrán el bloque `backend "s3"` sin la línea `bucket = "..."`.
   - Se inyectará en runtime usando: `terraform init -backend-config=backend.tfbackend`.
   - La herramienta `env-sync` o el bootstrap genera el archivo `backend.tfbackend` (`bucket = "..."`) en la carpeta del módulo.
   - El archivo `backend.tfbackend` está listado en `.gitignore`. Esto evita completamente diffs sucios en Git.

2. **Estructura del Directorio `environments/` en la Raíz (Aprobado):**
   ```text
   cleanmybelly/
   ├── environments/
   │   ├── global/
   │   │   ├── .env.bootstrap.example ──(cp)──> .env.bootstrap (PAT, Repo Name, OIDC)
   │   │   └── .env.shared.example    ──(cp)──> .env.shared    (Región, Dominio, Remote State Bucket)
   │   ├── dev/
   │   │   └── .env.dev.example       ──(cp)──> .env.dev       (DynamoDB dev, Frontend dev)
   │   └── prod/
   │       └── .env.prod.example      ──(cp)──> .env.prod      (DynamoDB prod, Frontend prod)
   ```

3. **Arquitectura Híbrida de `env-sync` (`tools/env_sync.py`) (Aprobado):**
   - Usa un archivo `mapping.py` declarativo para variables compartidas/globales (`PROJECT_NAME`, `AWS_REGION`, `HOSTED_ZONE_NAME`, `TERRAFORM_STATE_BUCKET`). Permite escribir la variable **una sola vez** en el `.env` y propagarla a múltiples módulos (Fan-out) con traducciones exactas de nombres (`tf_var`).
   - Usa auto-descubrimiento leyendo los `variables.tf` para mapear de forma segura variables específicas.
   - Permite prefijos por módulo (`DEV_BACKEND_...`, `PROD_FRONTEND_...`) cuando se agregan variables totalmente nuevas desde el `.env`.

---

## 4. Archivos Creados en `llm-context/2026-08-12/` para la Transición

- `llm-context/2026-08-12/context_export.md` (Este archivo con el resumen técnico de contexto).
- `llm-context/2026-08-12/initial_request.md` (La solicitud inicial del usuario redactada y pulida).
- `llm-context/2026-08-12/master_refactor_plan.md` (El plan maestro definitivo indicando lo aprobado, lo propuesto y las preguntas pendientes).

---

## 5. Instrucciones para la IA en la Nueva Ventana de Chat

1. Lee `llm-context/2026-08-12/context_export.md` y `llm-context/2026-08-12/master_refactor_plan.md`.
2. Confirma al usuario que tienes todo el contexto cargado.
3. Pregunta al usuario si desea comenzar con la ejecución del **Paso 1** (Crear `aws/pre-infra/bootstrap/providers.tf` y limpiar hardcodes en `variables.tf`).
