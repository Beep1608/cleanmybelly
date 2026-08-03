# Operations: GitHub Personal Access Token (PAT) Setup

This operational guide provides step-by-step instructions for creating a GitHub Personal Access Token (PAT) required during Phase 0 infrastructure bootstrapping and Terraform GitHub provider execution.

---

## 1. Overview & Required Token Scopes

The **cleanmybelly** infrastructure deployment uses Terraform to automate GitHub repository setup, CI/CD secrets configuration, and workflow publishing (in `aws/pre-infra/github/*`). To allow Terraform to manage these resources, you must supply a Personal Access Token with appropriate administrative permissions.

### Required Scopes Summary

* **Classic PAT Scopes**:
  * `repo` (Full control of private repositories: code, commit statuses, repository invites, collaborators, hooks, and settings).
  * `workflow` (Allows adding and updating GitHub Actions workflow files).
* **Fine-Grained PAT Permissions** (Repository Level):
  * **Administration**: Read and Write
  * **Contents**: Read and Write
  * **Secrets**: Read and Write
  * **Workflows**: Read and Write

---

## 2. Generating a Classic Personal Access Token (Recommended)

1. Log into your account on [GitHub](https://github.com/).
2. Click your profile icon in the upper-right corner and select **Settings**.
3. Scroll down the left sidebar and click **Developer settings**.
4. In the left sidebar, expand **Personal access tokens** and select **Tokens (classic)**.
5. Click the **Generate new token** dropdown and select **Generate new token (classic)**.
6. Authenticate with your GitHub password or 2FA if prompted.
7. Configure token settings:
   * **Note**: Enter a descriptive name (e.g. `cleanmybelly-terraform-bootstrap`).
   * **Expiration**: Select your preferred expiration period (e.g. `30 days` or `90 days`).
   * **Select scopes**: Check the following checkboxes:
     * `repo` (Selects all sub-items: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`)
     * `workflow`
8. Scroll to the bottom of the page and click **Generate token**.
9. **Copy the generated token immediately**. 

> ⚠️ **IMPORTANT SECURITY WARNING**:
> GitHub only displays the token once upon creation. Copy and store it securely in a password manager (e.g. 1Password, Bitwarden, or AWS SSM Parameter Store). Never commit your token to git or share it in public channels.

---

## 3. Generating a Fine-Grained Personal Access Token (Alternative)

If your organization enforces fine-grained access tokens:

1. Under **Developer settings** -> **Personal access tokens**, select **Fine-grained tokens**.
2. Click **Generate new token**.
3. Set **Token name**, **Expiration**, and **Repository access** (select *Only select repositories* -> `cleanmybelly`).
4. Under **Repository permissions**, grant **Access: Read and Write** to:
   * **Administration**
   * **Contents**
   * **Secrets**
   * **Workflows**
5. Click **Generate token** and save the token string.

---

## 4. Referencing the Token in Terraform Commands

During Phase 0 bootstrapping, pass your generated PAT token to Terraform using the `-var` flag:

```bash
cd aws/pre-infra/github/repository
terraform init
terraform apply -var="github_token=ghp_yourGeneratedTokenHere..."
```

Alternatively, export the token as an environment variable (`GITHUB_TOKEN`), allowing Terraform's GitHub provider to pick it up automatically without passing CLI flags:

```bash
export GITHUB_TOKEN="ghp_yourGeneratedTokenHere..."
terraform apply
```
