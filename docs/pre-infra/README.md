# Pre-Infra Setup (cleanmybelly)

This directory contains the bootstrap Terraform configuration required to set up the remote S3 state bucket and the programmatic deployer IAM user (`terraform-deployer`) for the **cleanmybelly** project.

State locking is managed natively by AWS S3 conditional writes, which requires Terraform 1.10+. No DynamoDB table is needed.

---

## 1. Deploying the Bootstrap Infrastructure

To create the backend resources and the automation user, run the following commands:

> [!NOTE]
> Ensure you are logged into your primary AWS administrative account in your terminal. Verify with:
> `aws configure list`

1. Navigate to this directory:
   ```bash
   cd pre-infra
   ```

2. Initialize Terraform (this runs with a local state backend):
   ```bash
   terraform init
   ```

3. Create the execution plan and apply it:
   ```bash
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```

4. Retrieve and save the generated credentials for the `terraform-deployer` automation user:
   ```bash
   terraform output -raw deployer_access_key_id
   terraform output -raw deployer_secret_access_key
   ```
   *(Keep the secret access key secure.)*

5. Retrieve and save the name of the created S3 state bucket:
   ```bash
   terraform output -raw terraform_state_bucket_name
   ```

---

## 2. Configuring the `/infra` Directory

After generating the credentials, configure the programmatic profile on your local machine to deploy the main infrastructure.

1. Configure a new AWS profile named `terraform-user` using the credentials obtained in the previous step:
   ```bash
   aws configure --profile terraform-user
   ```
   *   **Access Key ID**: `<deployer_access_key_id>`
   *   **Secret Access Key**: `<deployer_secret_access_key>`
   *   **Default region name**: `us-east-1` (or your preferred region)
   *   **Default output format**: `json`

2. Verify the profile is configured correctly:
   ```bash
   aws configure list --profile terraform-user
   ```

3. In your main `/infra` directory's `main.tf` file, configure the backend block to use the newly created S3 bucket and enable native S3 locking with `use_lockfile = true`:
   ```hcl
   terraform {
     required_version = ">= 1.10.0"

     required_providers {
       aws = {
         source  = "hashicorp/aws"
         version = "~> 6.0"
       }
     }

     backend "s3" {
       bucket       = "<YOUR_GENERATED_BUCKET_NAME>"
       key          = "cleanmybelly/infra/terraform.tfstate"
       region       = "us-east-1"
       encrypt      = true
       use_lockfile = true  # Enables native S3 state locking
       profile      = "terraform-user"
     }
   }
   ```

