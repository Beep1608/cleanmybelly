# Arquitectura AWS - Guía de Navegación

Esta carpeta contiene la documentación detallada de la infraestructura Cloud Serverless para el proyecto **cleanmybelly**. La arquitectura está dividida de forma lógica para permitir un mantenimiento independiente del frontend (distribución de contenido estático) y del backend (procesamiento lógico y base de datos).

---

## 🗺️ Mapa de Documentación

Para explorar los diferentes componentes de la infraestructura, selecciona una de las siguientes guías:

| Documento | Descripción | Enfoque |
| :--- | :--- | :--- |
| 📖 [1. General](file:///home/jose-lopez-lara/Git/cleanmybelly/aws/docs/general.md) | Vista panorámica de todos los servicios de AWS utilizados en el proyecto. | Todos los servicios de AWS |
| ⚙️ [2. Backend](file:///home/jose-lopez-lara/Git/cleanmybelly/aws/docs/backend.md) | Detalle del flujo de cómputo serverless y persistencia de datos. Incluye diagrama de flujo. | Route 53, ACM, API Gateway, Lambda, DynamoDB, CloudWatch, IAM |
| 🎨 [3. Frontend](file:///home/jose-lopez-lara/Git/cleanmybelly/aws/docs/frontend.md) | Detalle de la distribución global de archivos estáticos (Client-Side Rendering). Incluye diagrama de flujo. | Route 53, ACM, CloudFront, S3 |

---

## 🔍 Flujo Global de Navegación de Datos

El siguiente diagrama ilustra cómo se bifurcan las peticiones del usuario final según el tipo de interacción (acceso al sitio web vs. envío de información al backend):

```mermaid
graph TD
    User([Usuario en Navegador]) -->|1. Solicita Sitio Web| DNS_Front[Route 53: Domain]
    User -->|2. Envía Formulario| DNS_Back[Route 53: Subdomain api.*]

    subgraph Flujo Frontend (Estático)
        DNS_Front --> CF[Amazon CloudFront]
        CF -.->|Cifrado HTTPS| ACM_CF[AWS Certificate Manager]
        CF -->|Lee archivos| S3[Amazon S3 Bucket]
    end

    subgraph Flujo Backend (Cómputo)
        DNS_Back --> APIGW[Amazon API Gateway]
        APIGW -.->|Cifrado HTTPS| ACM_APIGW[AWS Certificate Manager]
        APIGW -->|Invoca| Lambda[AWS Lambda]
        Lambda -.->|Seguridad| IAM[AWS IAM Role]
        Lambda -->|Escribe logs| CW[Amazon CloudWatch]
        Lambda -->|Guarda Datos| Dynamo[Amazon DynamoDB]
    end

    style S3 fill:#E0F7FA,stroke:#00ACC1,stroke-width:2px
    style CF fill:#E8EAF6,stroke:#3F51B5,stroke-width:2px
    style APIGW fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px
    style Lambda fill:#FFF3E0,stroke:#FB8C00,stroke-width:2px
    style Dynamo fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
```
