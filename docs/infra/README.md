# AWS Architecture - Navigation Guide

This directory contains the detailed documentation of the Serverless Cloud infrastructure for the **cleanmybelly** project. The architecture is logically divided to allow independent maintenance of the frontend (static content distribution) and the backend (processing logic and database).

---

## Documentation Map

To explore the different infrastructure components, select one of the following guides:

| Document | Description | Focus |
| :--- | :--- | :--- |
| [1. General](general.md) | High-level overview of all AWS services used in the project. | All AWS services |
| [2. Backend](backend.md) | Details of the serverless computing flow and data persistence. Includes flowchart. | Route 53, ACM, API Gateway, Lambda, DynamoDB, CloudWatch, IAM |
| [3. Frontend](frontend.md) | Details of the global static file distribution (Client-Side Rendering). Includes flowchart. | Route 53, ACM, CloudFront, S3 |
| [4. Planning](planning.md) | Environment configuration, directory setup, modular separation, and cross-referencing. | Terraform folder structures, modules, dev/prod isolation |
| [5. Deployment](deployment.md) | Step-by-step setup sequence, secrets lookup with SSM, and cache invalidation. | Setup order, CLI commands, GitHub Actions, Parameter Store |

---

## Global Data Flow

The following diagram illustrates how end-user requests branch based on the type of interaction (accessing the website vs. sending information to the backend):

```mermaid
graph TD
    User([User in Browser]) -->|1. Requests Website| DNS_Front[Route 53: Domain]
    User -->|2. Submits Form| DNS_Back[Route 53: Subdomain api.*]

    subgraph "Frontend Flow (Static)"
        DNS_Front --> CF[Amazon CloudFront]
        CF -.->|HTTPS Encryption| ACM_CF[AWS Certificate Manager]
        CF -->|Reads files| S3[Amazon S3 Bucket]
    end

    subgraph "Backend Flow (Compute)"
        DNS_Back --> APIGW[Amazon API Gateway]
        APIGW -.->|HTTPS Encryption| ACM_APIGW[AWS Certificate Manager]
        APIGW -->|Invokes| Lambda[AWS Lambda]
        Lambda -.->|Security| IAM[AWS IAM Role]
        Lambda -->|Writes logs| CW[Amazon CloudWatch]
        Lambda -->|Saves Data| Dynamo[Amazon DynamoDB]
    end

    style S3 fill:#E0F7FA,stroke:#00ACC1,stroke-width:2px
    style CF fill:#E8EAF6,stroke:#3F51B5,stroke-width:2px
    style APIGW fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px
    style Lambda fill:#FFF3E0,stroke:#FB8C00,stroke-width:2px
    style Dynamo fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
```
