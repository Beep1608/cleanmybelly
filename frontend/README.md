# Next.js Frontend Initialization Guide

This directory contains the Client-Side Rendered (CSR) frontend application for the **cleanmybelly** project. The frontend is built using **Next.js** and is designed to compile to a static export (`output: 'export'`) to be hosted on AWS S3 and distributed globally via Amazon CloudFront.

---

## 1. Initializing the Next.js Project

Since this directory already contains this guide, running `create-next-app` in the current folder might warn you that the directory is not empty. Follow these steps to initialize the project correctly:

### Step 1: Run the Next.js Bootstrapper
From the **root directory** of the repository (not inside `/frontend`), run the following command to bootstrap Next.js in a clean subfolder:
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```
*If prompted to proceed, type `y`.*

> [!NOTE]
> If the command prompts that the folder already exists, you can temporarily move this `README.md` to another folder, run the bootstrap command, and then restore this `README.md` back to the `/frontend` directory.

### Step 2: Verify the Directory Structure
After initialization, your `/frontend` folder structure should look like this:
```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── ...
├── next.config.mjs
├── tsconfig.json
├── package.json
└── README.md (This file)
```

---

## 2. Configuring Next.js for Static S3 Hosting

AWS S3 static website hosting and CloudFront OAC require static resources (HTML, CSS, JS, and images). You must configure Next.js for static HTML export.

1. Open the `next.config.mjs` (or `next.config.js`) file in the `/frontend` directory.
2. Update the configuration to include the `output: 'export'` parameter and disable image optimization (since S3 doesn't run a Node server to optimize images dynamically):

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true // Required for static exports
  }
};

export default nextConfig;
```

---

## 3. Development Workflow

### Run the App Locally
Run the development server to preview changes in real time:
```bash
cd frontend
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build the Static Site Locally
Before deploying, compile your application and generate the static export:
```bash
npm run build
```
This command compiles your Next.js application and creates a new directory named **`out/`** in `/frontend`. This `out/` folder contains the static HTML pages, CSS files, and JS chunks ready to be uploaded to AWS S3.

---

## 4. Manual Deployment (AWS CLI)

To deploy your static frontend changes manually to S3 and CloudFront:

1. **Build the static files**:
   ```bash
   npm run build
   ```
2. **Synchronize the `out/` directory to S3**:
   *(Retrieve the S3 bucket name from the Terraform outputs in `aws/infra/environments/dev/frontend`)*:
   ```bash
   aws s3 sync ./out s3://<your-s3-frontend-bucket-name> --delete
   ```
3. **Invalidate CloudFront Cache**:
   *(Retrieve the CloudFront Distribution ID from the Terraform outputs)*:
   ```bash
   aws cloudfront create-invalidation --distribution-id <your-cloudfront-id> --paths "/*"
   ```

---

## 5. Automated Deployment (CI/CD)

The GitHub Actions workflow under `.github/workflows/deploy-frontend.yml` is configured to automatically build and deploy this Next.js app to S3 whenever changes are pushed to `main` inside the `/frontend` directory. 

For pipeline configuration details, consult the [CI/CD Pipelines Manual](../docs/manuals/pipelines/README.md).
