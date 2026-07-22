# Operations: Domain Delegation (Namecheap to AWS Route 53)

This guide explains how to delegate a custom domain purchased at **Namecheap** to **AWS Route 53** using Nameserver (NS) records.

---

## Execution Sequence

```mermaid
graph TD
    Phase1[1. Deploy Route 53 DNS Zone] --> Phase2[2. Retrieve AWS Name Servers]
    Phase2 --> Phase3[3. Set Custom DNS in Namecheap]
    Phase3 --> Phase4[4. Verify Propagation & Deploy ACM SSL]
```

---

## Step 1: Deploy Route 53 DNS Zone

1. Navigate to:
   ```bash
   cd aws/infra/shared/networking/dns-zone
   ```
2. Initialize and apply:
   ```bash
   terraform init
   terraform apply
   ```

---

## Step 2: Retrieve AWS Name Servers

Run `terraform output` to display the assigned AWS Name Servers:

```hcl
name_servers = [
  "ns-1025.awsdns-00.org",
  "ns-154.awsdns-19.com",
  "ns-782.awsdns-33.net",
  "ns-1981.awsdns-56.co.uk"
]
```

Copy the 4 server addresses (excluding quotes).

---

## Step 3: Configure Custom DNS in Namecheap

1. Log into your [Namecheap Account](https://www.namecheap.com/).
2. Navigate to **Domain List** -> Click **Manage** next to your domain (`cleanmybelly.com`).
3. Scroll to **NAMESERVERS** section.
4. Switch dropdown from *Namecheap BasicDNS* to **Custom DNS**.
5. Paste the 4 AWS Name Servers into lines 1 through 4.
6. Click the green checkmark to save.

---

## Step 4: Verify Propagation & Deploy SSL Certificates

1. Verify DNS delegation using terminal `dig`:
   ```bash
   dig cleanmybelly.com NS
   ```
2. Once the NS records resolve to AWS, deploy SSL certificates:
   ```bash
   cd ../certificates
   terraform init
   terraform apply
   ```
   *(ACM validation completes automatically in 2 to 5 minutes).*

---

## ACM SSL Validation Architecture

```mermaid
graph TD
    subgraph DNS_Zone["1. DNS Zone (dns-zone)"]
        HZ["aws_route53_zone.primary"]
    end

    subgraph Certificates["2. Certificates (certificates)"]
        DS_HZ["data.aws_route53_zone.primary"]
        ACM["aws_acm_certificate.dev_frontend"]
        REC["aws_route53_record.dev_frontend_validation"]
        VAL["aws_acm_certificate_validation.dev_frontend"]
    end

    subgraph Frontend_Env["3. Frontend Env (dev/frontend)"]
        CF["aws_cloudfront_distribution"]
    end

    HZ -->|1. Resolves zone_id| DS_HZ
    DS_HZ -->|2. Provides zone_id| REC
    ACM -->|3. Provides CNAME record| REC
    REC -->|4. Writes record| HZ
    ACM -->|5. Exports ARN| VAL
    VAL -->|6. Validates certificate| ACM
    ACM -->|7. Binds SSL| CF
```
