# Operations: Static Asset Sync & CDN Cache Invalidation

This guide documents how to manually upload frontend assets to Amazon S3 and invalidate the CloudFront edge cache.

---

## Manual Sync & Invalidation Steps

When making visual UI or client-side JavaScript changes without triggering CI/CD pipelines, execute the following commands:

1. **Build Static Web Assets**:
   ```bash
   cd app/frontend
   npm ci
   npm run build # Generates static files in app/frontend/out
   ```

2. **Sync Compiled Assets to S3**:
   ```bash
   aws s3 sync ./out s3://<S3_FRONTEND_BUCKET_NAME> --delete --profile terraform-user
   ```

3. **Invalidate CloudFront Edge Cache**:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id <CLOUDFRONT_DISTRIBUTION_ID> \
     --paths "/*" \
     --profile terraform-user
   ```

---

## Automated CI/CD Execution

For automated deployments on `git push`, refer to the [Monorepo Pipeline Reference](reference/github_actions_monorepo.md).
