# Operations: Application Secrets Management (SSM Parameter Store)

This guide documents how to create, update, and manage application secrets for the **cleanmybelly** backend using **AWS Systems Manager (SSM) Parameter Store**.

---

## Overview & Security Policy

Secrets and sensitive API credentials (e.g. Stripe keys, SMTP passwords, third-party tokens) are stored as encrypted `SecureString` parameters in SSM Parameter Store. 

Lambda execution roles are granted read-only access to parameters following the naming pattern:
```text
/${PROJECT}/${ENVIRONMENT}/${SECRET_NAME}
# Example: /cleanmybelly/dev/stripe_secret_key
```

---

## Creating / Updating a Secret

### Option A: AWS CLI (Recommended)

Run the following command in your terminal:
```bash
aws ssm put-parameter \
  --name "/cleanmybelly/dev/stripe_secret_key" \
  --value "sk_test_51NxXxXxXx..." \
  --type "SecureString" \
  --overwrite \
  --profile terraform-user
```

### Option B: AWS Web Console

1. Navigate to **AWS Systems Manager** -> **Parameter Store**.
2. Click **Create Parameter**.
3. Set **Name** to `/{project_name}/{environment}/{secret_name}` (e.g. `/cleanmybelly/dev/stripe_secret_key`).
4. Select **Type**: `SecureString`.
5. Enter secret value under **Value** and save.

---

## Fetching Secrets in Lambda Code (Node.js)

Your Lambda backend retrieves secrets dynamically at runtime without hardcoding sensitive strings:

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

// Handler Usage:
// const stripeKey = await getSecret("stripe_secret_key");
```
