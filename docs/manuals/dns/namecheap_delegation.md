# Custom Domain Delegation: Namecheap to AWS Route 53

This manual explains how to delegate your custom domain purchased at **Namecheap** to **AWS Route 53** using Nameserver (NS) records. This is the recommended practice to enable automatic SSL certificate validation (ACM) and fast DNS alias routing to AWS resources.

---

## 1. Retrieve the AWS Nameservers

Once you apply your shared networking infrastructure, AWS Route 53 creates your Hosted Zone. This Hosted Zone automatically generates a set of 4 unique Nameservers (NS records).

You can retrieve these nameservers in two ways:

### Method A: Via Terraform Output (Recommended)
Navigate to your shared networking folder and read the state outputs:
```bash
cd aws/infra/shared/networking
terraform output -json
```
In the outputs, look for the `nameservers` list or inspect the state directly to copy the four NS endpoints.

### Method B: Via AWS Console
1. Log in to your AWS Console.
2. Navigate to **Route 53** -> **Hosted Zones** and click on your domain name (e.g., `cleanmybelly.com`).
3. In the records list, find the record of type **NS**.
4. You will see four values, looking similar to:
   * `ns-1025.awsdns-00.org.`
   * `ns-154.awsdns-19.com.`
   * `ns-782.awsdns-33.net.`
   * `ns-1981.awsdns-56.co.uk.`
5. **Copy these four lines** (exclude the trailing dot `.` at the end of each server name when pasting in Namecheap if the UI doesn't support it, though Namecheap usually accepts them).

---

## 2. Configure Custom DNS in Namecheap

Now that you have the AWS nameserver addresses, you need to update your domain's settings in your Namecheap account:

1. Log in to [Namecheap.com](https://www.namecheap.com/).
2. Click on **Domain List** in the left sidebar.
3. Locate your domain (e.g., `cleanmybelly.com`) and click the **Manage** button on the right.
4. Scroll down to the **NAMESERVERS** section.
5. Change the dropdown from *Namecheap BasicDNS* (or *Namecheap WebDNS*) to **Custom DNS**.
6. Paste the four AWS Nameserver addresses you copied in the previous step into the empty input fields:
   * *Line 1*: `ns-1025.awsdns-00.org`
   * *Line 2*: `ns-154.awsdns-19.com`
   * *Line 3*: `ns-782.awsdns-33.net`
   * *Line 4*: `ns-1981.awsdns-56.co.uk`
7. Click the **green checkmark icon** (Save) next to the input fields to save the changes.

---

## 3. Verify DNS Propagation

DNS propagation refers to the time it takes for servers across the internet to realize that DNS authority has moved to AWS.

* **Timeframe**: Propagation usually takes between **5 minutes to 2 hours**, but can take up to 24-48 hours in rare cases.
* **Testing Propagation**:
  You can run a query in your terminal using `dig` or `nslookup` to see which nameservers are currently resolving your domain:
  ```bash
  dig cleanmybelly.com NS
  ```
  Check the `ANSWER SECTION` or `AUTHORITY SECTION`. You should see the `awsdns` servers listed.
* **Online Tool**: You can also use public DNS lookup checkers like [DNSChecker.org](https://dnschecker.org/) and search for your domain's **NS** records.
