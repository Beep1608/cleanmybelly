# Solicitud Inicial del Usuario: Refactorización de Variables Terraform & Tool env-sync

> **Nota:** Este documento contiene la solicitud inicial formulada por el usuario para el análisis y diseño de la refactorización de la infraestructura Terraform y la creación de la herramienta de gestión unificada de variables.

---

## Solicitud Original (Redacción Pulida)

Si analizas `aws/pre-infra/bootstrap`, este posee una arquitectura en la que se espera el uso de un archivo `terraform.tfvars`, creado mediante una copia de `aws/pre-infra/bootstrap/terraform.tfvars.example`. 

Requiero crear un **plan estratégico (artefacto)** que considere los siguientes requerimientos:

---

### Requerimientos Principales

1. **Análisis de Directorios e Identificación de Variables Hardcodeadas:**
   - Analizar cada uno de los diferentes directorios dentro de `aws/pre-infra` y `aws/infra`.
   - Eliminar y evitar el uso de variables hardcodeadas directamente dentro de los archivos `.tf`.

2. **Estandarización de `variables.tf` y `terraform.tfvars.example`:**
   - Todas las variables deben estar formalmente declaradas dentro de su respectivo `variables.tf`.
   - Cada módulo debe contar con un archivo `terraform.tfvars.example` asociado.
   - Esto incluye variables sensibles (como el Personal Access Token de GitHub `GITHUB_TOKEN`), asegurando que todos los archivos `terraform.tfvars` reales estén listados en el `.gitignore`.

3. **Creación e Integración de la Nueva Herramienta `env-sync` (`tools/env_sync.py`):**
   - Integrar una nueva herramienta encargada de realizar la copia (`cp`) de los archivos `.example` a los `.tfvars` reales en caso de que el proyecto haya sido clonado por primera vez y la copia aún no exista.
   - La herramienta debe mantener todas las variables al día de manera consolidada desde **un único lugar centralizado (archivos de entorno `.env`)**.
   - **Comportamiento al ejecutar el script principal (`python3 tools/env_sync.py`):**
     - Efectuar un análisis y determinar si se debe realizar el `cp` si solo existe el archivo `.example`.
     - Analizar si están al día el `variables.tf` `.example`, el `terraform.tfvars` asociado y los archivos consolidadores `.env`.
   - **Consolidación Centralizada:** Planificar cómo consolidar la configuración para que el desarrollador únicamente modifique el archivo `.env` correspondiente, permitiendo que la herramienta sepa a qué directorio, archivo `variables.tf`, `terraform.tfvars` y `.example` debe aplicar las modificaciones.
   - **Reusabilidad:** Esta herramienta será consumida por `tools/bootstrap.py` (y sus módulos en `tools/modules/bootstrap`) en una etapa inicial durante la Fase 2, pero también podrá ser ejecutada de forma independiente cada vez que el usuario agregue una variable nueva o modifique las existentes en los archivos `.env` (actuando como un proceso de *update/create inteligente*).

---

### Validaciones Adicionales

1. **Verificación de `providers.tf` en todos los Root Modules:**
   - Dado que se está realizando el análisis integral de la infraestructura, se debe corroborar que **todos los directorios tengan su archivo `providers.tf` dedicado**.
   - Algunos directorios carecen de `providers.tf` y mantienen el bloque `terraform {}` o `provider {}` dentro de `main.tf` u otros archivos `.tf`.

---

### Consideraciones Técnicas a Planear / Solventar Antes de Comenzar

1. **Optimización del Find & Replace en Fase 2 de Bootstrap (`phase_02_find_replace.py`):**
   - Actualmente, la Fase 2 del bootstrap realiza una modificación mediante *find & replace* reemplazando el placeholder `<TERRAFORM_STATE_BUCKET_NAME>` en múltiples archivos `.tf` por el nombre del bucket S3 remoto generado.
   - Esto genera cambios y diffs sucios en el directorio de trabajo de Git desde el primer momento.
   - Se requiere evaluar las mejores prácticas de Terraform (por ejemplo, Partial Backend Configuration mediante `-backend-config`) para evitar mutar archivos `.tf` rastreados por Git y reducir la cantidad de archivos afectados.
