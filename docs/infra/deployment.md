# AWS Infrastructure Deployment Guide (cleanmybelly)

This manual provides step-by-step instructions to deploy the serverless infrastructure, manage application secrets, and upload frontend updates for the **cleanmybelly** project.

---

## Prerequisites

Before beginning, ensure:
1. **Bootstrap Setup Completed**: You have successfully executed the steps in [docs/pre-infra/README.md](../pre-infra/README.md).
2. **AWS Profile Configured**: You have your local profile `terraform-user` configured with the programmatic access keys of `terraform-deployer`.
3. **Bucket Name ready**: You have the name of the generated S3 remote state bucket (e.g., `cleanmybelly-tfstate-v1-bb8f23ca`).
4. **Terraform CLI**: Installed version is `>= 1.10.0`.

---

## 1. Global Deployment Sequence

Because frontend environments depend on backend URLs, and both depend on Route 53 Hosted Zones and certificates, you **must** follow this strict order of execution:

`[Step 1A: DNS Zone (Route 53)]` &rarr; `[Step 1B: Registrar update (Namecheap)]` &rarr; `[Step 1C: SSL Certificates (ACM)]` &rarr; `[Step 2: Environment Backend (dev/prod)]` &rarr; `[Step 3: Environment Frontend (dev/prod)]`

---

### Step 1A: Deploy DNS Zone (Route 53)

This step creates the base Route 53 Hosted Zone and outputs the Name Servers assigned by AWS.

1. Navigate to the DNS Zone folder:
   ```bash
   cd aws/infra/shared/networking/dns-zone
   ```

2. Open [providers.tf](../../aws/infra/shared/networking/dns-zone/providers.tf) and replace the bucket name placeholder:
   ```hcl
   backend "s3" {
     bucket = "cleanmybelly-tfstate-v1-bb8f23ca" # Ensure this matches your S3 remote state bucket name
     # ...
   }
   ```

3. Initialize and apply:
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```
   Save the **Name Servers** (`name_servers`) listed in the outputs. You will need to delegate your domain to these servers.

---

### Step 1B: Delegate Custom Domain (Registrar Setup)

Update your domain registrar settings (e.g., Namecheap) to point to the newly generated Route 53 Name Servers.
Refer to the detailed guide: [docs/manuals/dns/README.md](../manuals/dns/README.md).

*(Note: Wait for DNS propagation, which typically takes between 5 minutes to 2 hours, before continuing to the next step).*

---

### Step 1C: Deploy SSL Certificates (ACM & Validation)

Once domain delegation has propagated, you can request and validate your SSL certificates.

1. Navigate to the certificates folder:
   ```bash
   cd ../certificates
   ```

2. Open [providers.tf](../../aws/infra/shared/networking/certificates/providers.tf) and replace the bucket name placeholder:
   ```hcl
   backend "s3" {
     bucket = "cleanmybelly-tfstate-v1-bb8f23ca" # Ensure this matches your S3 remote state bucket name
     # ...
   }
   ```

3. Initialize and apply:
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```
   *(Note: This step automatically creates DNS validation records in Route 53 and waits for ACM validation to complete. Since your domain is already delegated, this will succeed in 2-5 minutes).*

---

### Step 2: Deploy Backend Environment (dev or prod)

Deploy compute resources (Lambda), databases (DynamoDB), and HTTP gateways (API Gateway).

1. Choose your environment folder (e.g. `dev`):
   ```bash
   cd ../../../environments/dev/backend
   ```

2. Open [providers.tf](../../aws/infra/environments/dev/backend/providers.tf) and replace the backend bucket name placeholder:
   ```hcl
   backend "s3" {
     bucket = "cleanmybelly-tfstate-v1-bb8f23ca"
     # ...
   }
   ```

3. Open [main.tf](../../aws/infra/environments/dev/backend/main.tf). Replace the backend bucket name in `data.terraform_remote_state.networking` config block:
   ```hcl
   data "terraform_remote_state" "networking" {
     backend = "s3"
     config = {
       bucket = "cleanmybelly-tfstate-v1-bb8f23ca"
       # ...
     }
   }
   ```

4. Prepare your Lambda distribution package:
   - Ensure your backend code is compiled.
   - Replace the `placeholder.zip` file referenced in `main.tf` with your actual lambda code package zip, or adjust the path in `main.tf`:
   ```hcl
   lambda_zip_path = "${path.module}/../../../../backend/dist/function.zip"
   ```

5. Initialize and apply:
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```

---

### Step 3: Deploy Frontend Environment (dev or prod)

Deploy static hosting (S3) and distribution CDN (CloudFront) linked to your custom domains.

1. Navigate to the frontend folder:
   ```bash
   cd ../frontend
   ```

2. Open [providers.tf](../../aws/infra/environments/dev/frontend/providers.tf) and update the bucket name in the `backend "s3"` block.

3. Open [main.tf](../../aws/infra/environments/dev/frontend/main.tf) and replace the bucket name placeholders in both `data.terraform_remote_state` blocks (`backend` and `networking`).

4. Initialize and apply:
   ```bash
   terraform init
   terraform plan -out plan.out
   terraform apply "plan.out"
   ```

---

## 2. Managing Application Secrets (SSM Parameter Store)

To keep the platform generic and costs at **$0 (Scale-To-Zero)**, secrets and credentials for third-party integrations (like Stripe, SMTP, etc.) are stored securely in **AWS Systems Manager (SSM) Parameter Store** using `SecureString` types. 

Your Lambda functions have read access to parameters matching the prefix `/${project_name}/${environment}/*` (e.g. `/cleanmybelly/dev/*`).

### Adding a Secret via AWS CLI
Run the following command in your terminal to save a secret:
```bash
aws ssm put-parameter \
  --name "/cleanmybelly/dev/stripe_secret_key" \
  --value "sk_test_51NxXxXxXx..." \
  --type "SecureString" \
  --overwrite \
  --profile terraform-user
```

### Adding a Secret via AWS Web Console
1. Navigate to **AWS Systems Manager** -> **Parameter Store**.
2. Click **Create Parameter**.
3. Set **Name** to `/{project_name}/{environment}/{secret_name}` (e.g., `/cleanmybelly/dev/stripe_secret_key`).
4. Under **Type**, choose **SecureString**.
5. Input your secret under **Value** and save.

### Accessing Secrets in Lambda Code (Node.js)
Your backend code can fetch parameters dynamically without hardcoding them:
```javascript
const { SSMClient, GetParameterCommand } = require("@aws-sdk/client-ssm");
const ssm = new SSMClient({ region: process.env.AWS_REGION || "us-east-1" });

async function getSecret(secretName) {
  const command = new GetParameterCommand({
    Name: `/${process.env.PROJECT}/${process.env.ENVIRONMENT}/${secretName}`,
    WithDecryption: true
  });
  const response = await ssm.send(command);
  return response.Parameter.Value;
}

// Usage in handler:
// const stripeKey = await getSecret("stripe_secret_key");
```

---

## 3. Frontend Updates and CDN Cache Invalidation

When you make visual changes or update your Client-Side Javascript, you need to sync files to S3 and invalidate the CloudFront CDN cache.

### Manual CDN Sync & Invalidation
Once `terraform apply` finishes, it outputs the S3 Bucket Name and CloudFront ID. You can run these commands manually:

1. **Upload Assets**:
   ```bash
   aws s3 sync ./frontend/dist s3://<s3_bucket_name_output> --delete
   ```
2. **Invalidate Cache**:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id <cloudfront_distribution_id_output> \
     --paths "/*"
   ```

### CI/CD Pipeline (GitHub Actions Blueprint)
If automating via GitHub Actions, extract outputs from Terraform and run:
```yaml
- name: Deploy Frontend to S3
  run: |
    aws s3 sync ./frontend/dist s3://${{ steps.tf_outputs.outputs.s3_bucket_name }} --delete

- name: Invalidate CloudFront Cache
  run: |
    aws cloudfront create-invalidation --distribution-id ${{ steps.tf_outputs.outputs.cloudfront_distribution_id }} --paths "/*"
```
