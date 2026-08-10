#!/usr/bin/env python3
"""
cleanmybelly Bootstrap CLI Tool

Automated Python CLI tool for end-to-end infrastructure bootstrapping on AWS & GitHub.
Provisions S3 remote state, IAM deployer, GitHub repository, OIDC federation,
workflow secrets, Route 53 DNS hosted zone, and ACM SSL certificates.

Usage:
    python3 tools/bootstrap.py
"""

import os
import sys
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

# --- ANSI Color Codes for Styled Terminal Output ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_header(title: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║  {title.ljust(75)} ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

def log_phase(phase_num: int, total_phases: int, title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}[PHASE {phase_num}/{total_phases}] {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'─' * 70}{Colors.RESET}")

def log_success(msg: str):
    print(f"  {Colors.GREEN}✓ {msg}{Colors.RESET}")

def log_info(msg: str):
    print(f"  {Colors.CYAN}ℹ {msg}{Colors.RESET}")

def log_warn(msg: str):
    print(f"  {Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def log_error(msg: str):
    print(f"  {Colors.RED}✗ {msg}{Colors.RESET}")

def run_cmd(cmd, cwd=None, env=None, capture_output=True, check=True):
    """Utility wrapper for subprocess execution."""
    try:
        res = subprocess.run(
            cmd,
            cwd=cwd,
            env=env or os.environ.copy(),
            capture_output=capture_output,
            text=True,
            check=check
        )
        return res
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        if e.stdout:
            print(f"{Colors.YELLOW}STDOUT:\n{e.stdout}{Colors.RESET}")
        if e.stderr:
            print(f"{Colors.RED}STDERR:\n{e.stderr}{Colors.RESET}")
        raise e

def find_repo_root() -> Path:
    """Finds repository root directory."""
    current = Path.cwd().resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "aws").exists():
            return parent
    return current

class BootstrapManager:
    def __init__(self):
        self.repo_root = find_repo_root()
        self.tools_dir = self.repo_root / "tools"
        self.outputs_file = self.tools_dir / "bootstrap_outputs.json"
        
        # User input configuration
        self.config = {
            "github_token": "",
            "github_org_or_username": "",
            "github_repo_name": "",
            "github_repo_visibility": "public",
            "domain_name": "",
            "aws_region": "us-east-1"
        }
        
        # Tracked outputs
        self.outputs = {
            "timestamp": "",
            "terraform_state_bucket": "",
            "iam_deployer_user": "terraform-deployer",
            "iam_deployer_access_key_id": "",
            "github_repository_url": "",
            "github_repository_full_name": "",
            "github_actions_role_arn": "",
            "route53_zone_id": "",
            "route53_name_servers": [],
            "acm_certificates": {}
        }

    # --------------------------------------------------------------------------
    # Check Prerequisites
    # --------------------------------------------------------------------------
    def verify_prerequisites(self):
        log_header("cleanmybelly Bootstrap CLI - Prerequisites Check")
        log_info(f"Repository Root: {self.repo_root}")

        # 1. Check Python version
        if sys.version_info < (3, 8):
            log_error(f"Python 3.8+ required. Current version: {sys.version}")
            sys.exit(1)
        log_success(f"Python {sys.version.split()[0]}")

        # 2. Check Terraform CLI
        if not shutil.which("terraform"):
            log_error("Terraform CLI not found in PATH. Please install Terraform >= 1.10.0.")
            sys.exit(1)
        res = run_cmd(["terraform", "version"])
        first_line = res.stdout.splitlines()[0] if res.stdout else "Terraform installed"
        log_success(f"Terraform: {first_line}")

        # 3. Check AWS CLI
        if not shutil.which("aws"):
            log_error("AWS CLI v2 not found in PATH. Please install AWS CLI v2.")
            sys.exit(1)
        res = run_cmd(["aws", "--version"])
        log_success(f"AWS CLI: {res.stdout.strip()}")

        # 4. Check AWS Credentials & Active Identity
        try:
            res = run_cmd(["aws", "sts", "get-caller-identity"])
            identity = json.loads(res.stdout)
            log_success(f"AWS Active Identity: {identity.get('Arn')}")
            log_info(f"AWS Account ID: {identity.get('Account')}")
        except Exception:
            log_error("No active AWS credentials found or identity check failed.")
            log_warn("Please run 'aws configure' or export AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY before running this tool.")
            sys.exit(1)

        # 5. Check Git
        if not shutil.which("git"):
            log_error("Git CLI not found in PATH.")
            sys.exit(1)
        log_success("Git CLI verified")

        # 6. Verify inside Git repository
        try:
            run_cmd(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.repo_root)
            log_success("Git repository verified")
        except Exception:
            log_error(f"{self.repo_root} is not a valid Git repository.")
            sys.exit(1)

        log_warn("Ensure your active AWS profile has Administrative access for initial bootstrapping.")

    # --------------------------------------------------------------------------
    # Collect Interactive User Inputs
    # --------------------------------------------------------------------------
    def collect_user_inputs(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}--- Configuration Inputs ---{Colors.RESET}\n")

        # 1. GitHub Token
        while True:
            token = input(f"{Colors.BOLD}Enter your GitHub Personal Access Token (PAT): {Colors.RESET}").strip()
            if token:
                self.config["github_token"] = token
                break
            log_error("GitHub PAT is required.")

        # 2. GitHub Username / Org
        default_user = "JoseLopezLara"
        try:
            res = run_cmd(["git", "config", "user.name"], check=False)
            if res.stdout and res.stdout.strip():
                default_user = res.stdout.strip()
        except Exception:
            pass

        user_input = input(f"{Colors.BOLD}Enter your GitHub username or organization [{default_user}]: {Colors.RESET}").strip()
        self.config["github_org_or_username"] = user_input if user_input else default_user

        # 3. GitHub Repo Name
        default_repo = self.repo_root.name
        repo_input = input(f"{Colors.BOLD}Enter target GitHub repository name [{default_repo}]: {Colors.RESET}").strip()
        self.config["github_repo_name"] = repo_input if repo_input else default_repo

        # 4. Repo Visibility
        vis_input = input(f"{Colors.BOLD}Enter repository visibility (public/private) [public]: {Colors.RESET}").strip().lower()
        self.config["github_repo_visibility"] = vis_input if vis_input in ["public", "private"] else "public"

        # 5. Domain Name
        while True:
            domain = input(f"{Colors.BOLD}Enter your root domain name (e.g. cleanmybelly.com): {Colors.RESET}").strip()
            if domain and "." in domain:
                self.config["domain_name"] = domain
                break
            log_error("Valid domain name is required (e.g. example.com).")

        # 6. AWS Region
        region_input = input(f"{Colors.BOLD}Enter AWS Region [us-east-1]: {Colors.RESET}").strip()
        self.config["aws_region"] = region_input if region_input else "us-east-1"

        print(f"\n{Colors.GREEN}✓ Configuration confirmed:{Colors.RESET}")
        print(f"  • GitHub Owner : {self.config['github_org_or_username']}")
        print(f"  • GitHub Repo  : {self.config['github_repo_name']} ({self.config['github_repo_visibility']})")
        print(f"  • Root Domain  : {self.config['domain_name']}")
        print(f"  • AWS Region   : {self.config['aws_region']}")

    # --------------------------------------------------------------------------
    # Phase 1: Bootstrap S3 Remote State Bucket
    # --------------------------------------------------------------------------
    def phase_1_bootstrap_s3(self):
        log_phase(1, 11, "Bootstrap S3 Remote State Bucket (pre-infra/bootstrap)")
        target_dir = self.repo_root / "aws/pre-infra/bootstrap"
        
        log_info("Initializing Terraform in aws/pre-infra/bootstrap...")
        run_cmd(["terraform", "init"], cwd=target_dir)

        log_info("Applying Terraform configuration...")
        run_cmd(["terraform", "apply", "-auto-approve"], cwd=target_dir)

        res = run_cmd(["terraform", "output", "-raw", "terraform_state_bucket_name"], cwd=target_dir)
        bucket_name = res.stdout.strip()
        self.outputs["terraform_state_bucket"] = bucket_name
        log_success(f"S3 Remote State Bucket Created: {bucket_name}")

    # --------------------------------------------------------------------------
    # Phase 2: Global Provider Configuration Find & Replace
    # --------------------------------------------------------------------------
    def phase_2_update_provider_bucket(self):
        log_phase(2, 11, "Global Find & Replace State Bucket Placeholder in providers.tf")
        bucket_name = self.outputs["terraform_state_bucket"]
        
        placeholders = [
            "<TERRAFORM_STATE_BUCKET_NAME>",
            "<YOUR_TFSTATE_BUCKET_NAME>",
            "<YOUR_GENERATED_BUCKET_NAME>"
        ]
        
        updated_count = 0
        aws_dir = self.repo_root / "aws"
        
        for tf_file in aws_dir.rglob("*.tf"):
            content = tf_file.read_text(encoding="utf-8")
            modified = False
            for ph in placeholders:
                if ph in content:
                    content = content.replace(ph, bucket_name)
                    modified = True
            if modified:
                tf_file.write_text(content, encoding="utf-8")
                updated_count += 1
                log_info(f"Updated: {tf_file.relative_to(self.repo_root)}")

        log_success(f"Updated state bucket in {updated_count} Terraform configuration files.")

    # --------------------------------------------------------------------------
    # Phase 3: Deploy IAM Local Deployer User
    # --------------------------------------------------------------------------
    def phase_3_deploy_iam_user(self):
        log_phase(3, 11, "Deploy IAM Deployer User (pre-infra/iam-deployer)")
        target_dir = self.repo_root / "aws/pre-infra/iam-deployer"

        log_info("Initializing Terraform...")
        run_cmd(["terraform", "init"], cwd=target_dir)

        log_info("Applying IAM deployer user configuration...")
        run_cmd(["terraform", "apply", "-auto-approve"], cwd=target_dir)

        res_id = run_cmd(["terraform", "output", "-raw", "deployer_access_key_id"], cwd=target_dir)
        res_secret = run_cmd(["terraform", "output", "-raw", "deployer_secret_access_key"], cwd=target_dir)

        self.outputs["iam_deployer_access_key_id"] = res_id.stdout.strip()
        self.outputs["iam_deployer_secret_access_key"] = res_secret.stdout.strip()
        log_success("IAM Deployer user and credentials generated.")

    # --------------------------------------------------------------------------
    # Phase 4: Configure AWS CLI Profile 'terraform-user'
    # --------------------------------------------------------------------------
    def phase_4_configure_aws_profile(self):
        log_phase(4, 11, "Configure Local AWS Profile 'terraform-user'")
        profile = "terraform-user"
        key_id = self.outputs["iam_deployer_access_key_id"]
        secret_key = self.outputs["iam_deployer_secret_access_key"]
        region = self.config["aws_region"]

        run_cmd(["aws", "configure", "set", "aws_access_key_id", key_id, "--profile", profile])
        run_cmd(["aws", "configure", "set", "aws_secret_access_key", secret_key, "--profile", profile])
        run_cmd(["aws", "configure", "set", "region", region, "--profile", profile])

        log_success(f"AWS CLI profile '{profile}' configured successfully.")

    # --------------------------------------------------------------------------
    # Phase 5: Provision GitHub Repository
    # --------------------------------------------------------------------------
    def phase_5_provision_github_repo(self):
        log_phase(5, 11, "Provision GitHub Repository (pre-infra/github/repository)")
        target_dir = self.repo_root / "aws/pre-infra/github/repository"

        log_info("Initializing Terraform...")
        run_cmd(["terraform", "init"], cwd=target_dir)

        log_info("Applying GitHub Repository resource...")
        tf_vars = [
            f"-var=github_token={self.config['github_token']}",
            f"-var=github_org_or_username={self.config['github_org_or_username']}",
            f"-var=github_repo_name={self.config['github_repo_name']}",
            f"-var=github_repo_visibility={self.config['github_repo_visibility']}"
        ]

        run_cmd(["terraform", "apply", "-auto-approve"] + tf_vars, cwd=target_dir)

        res_url = run_cmd(["terraform", "output", "-raw", "repository_html_url"], cwd=target_dir)
        res_full = run_cmd(["terraform", "output", "-raw", "repository_full_name"], cwd=target_dir)

        self.outputs["github_repository_url"] = res_url.stdout.strip()
        self.outputs["github_repository_full_name"] = res_full.stdout.strip()
        log_success(f"GitHub Repository Ready: {self.outputs['github_repository_full_name']}")

    # --------------------------------------------------------------------------
    # Phase 6: Connect Local Clone to Provisioned Repository
    # --------------------------------------------------------------------------
    def phase_6_connect_local_clone(self):
        log_phase(6, 11, "Connect Local Clone to Provisioned GitHub Repository")
        repo_url = self.outputs["github_repository_url"]
        git_remote_url = f"{repo_url}.git"

        log_info(f"Setting git remote origin to {git_remote_url}...")
        run_cmd(["git", "remote", "set-url", "origin", git_remote_url], cwd=self.repo_root)

        log_info("Pushing codebase to main branch...")
        try:
            run_cmd(["git", "push", "-u", "origin", "main"], cwd=self.repo_root)
            log_success("Codebase successfully pushed to new repository.")
        except Exception:
            log_warn("Initial push to main returned a non-zero code. Retrying with explicit ref...")
            run_cmd(["git", "push", "-u", "origin", "HEAD:refs/heads/main"], cwd=self.repo_root)
            log_success("Codebase pushed to main branch.")

    # --------------------------------------------------------------------------
    # Phase 7: Deploy OIDC Federation
    # --------------------------------------------------------------------------
    def phase_7_deploy_oidc(self):
        log_phase(7, 11, "Deploy GitHub OIDC Trust (pre-infra/github/oidc)")
        target_dir = self.repo_root / "aws/pre-infra/github/oidc"

        log_info("Initializing Terraform...")
        run_cmd(["terraform", "init"], cwd=target_dir)

        log_info("Applying OIDC trust configuration...")
        bucket_var = f"-var=terraform_state_bucket_name={self.outputs['terraform_state_bucket']}"
        run_cmd(["terraform", "apply", "-auto-approve", bucket_var], cwd=target_dir)

        res_role = run_cmd(["terraform", "output", "-raw", "github_actions_role_arn"], cwd=target_dir)
        self.outputs["github_actions_role_arn"] = res_role.stdout.strip()
        log_success(f"OIDC Role ARN: {self.outputs['github_actions_role_arn']}")

    # --------------------------------------------------------------------------
    # Phase 8: Deploy Secrets & Workflow
    # --------------------------------------------------------------------------
    def phase_8_deploy_secrets_workflow(self):
        log_phase(8, 11, "Deploy Secrets & Workflow Publishing (pre-infra/github/secrets-workflow)")
        target_dir = self.repo_root / "aws/pre-infra/github/secrets-workflow"

        log_info("Initializing Terraform...")
        run_cmd(["terraform", "init"], cwd=target_dir)

        log_info("Applying Secrets and Workflow Publishing...")
        tf_vars = [
            f"-var=github_token={self.config['github_token']}",
            f"-var=terraform_state_bucket_name={self.outputs['terraform_state_bucket']}",
            f"-var=github_org_or_username={self.config['github_org_or_username']}"
        ]

        run_cmd(["terraform", "apply", "-auto-approve"] + tf_vars, cwd=target_dir)
        log_success("GitHub Secrets and deployment workflow published successfully.")

    # --------------------------------------------------------------------------
    # Phase 9: Deploy DNS Zone
    # --------------------------------------------------------------------------
    def phase_9_deploy_dns_zone(self):
        log_phase(9, 11, "Deploy Route 53 Hosted Zone (infra/shared/networking/dns-zone)")
        target_dir = self.repo_root / "aws/infra/shared/networking/dns-zone"

        log_info("Initializing Terraform...")
        run_cmd(["terraform", "init"], cwd=target_dir)

        log_info("Applying Route 53 DNS Zone...")
        domain_var = f"-var=hosted_zone_name={self.config['domain_name']}"
        run_cmd(["terraform", "apply", "-auto-approve", domain_var], cwd=target_dir)

        res_zone = run_cmd(["terraform", "output", "-raw", "hosted_zone_id"], cwd=target_dir)
        res_ns = run_cmd(["terraform", "output", "-json", "name_servers"], cwd=target_dir)

        self.outputs["route53_zone_id"] = res_zone.stdout.strip()
        self.outputs["route53_name_servers"] = json.loads(res_ns.stdout)

        log_success(f"Route 53 Zone ID: {self.outputs['route53_zone_id']}")

    # --------------------------------------------------------------------------
    # Phase 10: Managed Pause for Manual Domain Registrar Setup & DNS Verification
    # --------------------------------------------------------------------------
    def phase_10_manual_registrar_pause(self):
        log_phase(10, 11, "Manual Domain Registrar Setup & Propagation Verification")
        name_servers = self.outputs["route53_name_servers"]
        domain = self.config["domain_name"]

        print(f"\n{Colors.BOLD}{Colors.YELLOW}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}║  ⚠ ACTION REQUIRED: CONFIGURE DOMAIN REGISTRAR NAME SERVERS                  ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        print(f"{Colors.YELLOW}║ Log into your domain registrar (e.g. Namecheap, GoDaddy, Route 53)           ║{Colors.RESET}")
        print(f"{Colors.YELLOW}║ for domain '{Colors.BOLD}{domain}{Colors.RESET}{Colors.YELLOW}' and update Custom DNS to these 4 Name Servers:  ║{Colors.RESET}")
        print(f"{Colors.YELLOW}║                                                                              ║{Colors.RESET}")
        for i, ns in enumerate(name_servers, 1):
            print(f"{Colors.YELLOW}║   {i}. {Colors.BOLD}{ns.ljust(68)}{Colors.RESET}{Colors.YELLOW} ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

        input(f"{Colors.BOLD}{Colors.CYAN}Press [ENTER] once you have updated your Name Servers at your registrar...{Colors.RESET}")

        log_info(f"Verifying DNS propagation for {domain}...")
        try:
            res = run_cmd(["dig", "+short", domain, "NS"], check=False)
            if res.stdout:
                log_success("DNS records retrieved via dig:")
                print(f"    {res.stdout.strip()}")
            else:
                log_warn("DNS propagation is still in progress. Continuing setup...")
        except Exception:
            log_warn("Unable to execute 'dig'. Continuing with certificate issuance...")

    # --------------------------------------------------------------------------
    # Phase 11: Deploy ACM SSL Certificates
    # --------------------------------------------------------------------------
    def phase_11_deploy_certificates(self):
        log_phase(11, 11, "Deploy ACM SSL Certificates (infra/shared/networking/certificates)")
        target_dir = self.repo_root / "aws/infra/shared/networking/certificates"

        log_info("Initializing Terraform...")
        run_cmd(["terraform", "init"], cwd=target_dir)

        log_info("Applying ACM Certificates and Route 53 DNS validation...")
        domain_var = f"-var=hosted_zone_name={self.config['domain_name']}"
        run_cmd(["terraform", "apply", "-auto-approve", domain_var], cwd=target_dir)

        # Retrieve Outputs
        certs = {}
        for output_key in ["dev_frontend_cert_arn", "dev_backend_cert_arn", "prod_frontend_cert_arn", "prod_backend_cert_arn"]:
            try:
                res = run_cmd(["terraform", "output", "-raw", output_key], cwd=target_dir, check=False)
                if res.stdout:
                    certs[output_key] = res.stdout.strip()
            except Exception:
                pass

        self.outputs["acm_certificates"] = certs
        log_success("ACM SSL Certificates issued and validated successfully.")

    # --------------------------------------------------------------------------
    # Save Outputs File & Summary
    # --------------------------------------------------------------------------
    def save_outputs_and_summary(self):
        self.outputs["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        # Save JSON file (ignoring sensitive plain secret key, keeping key ID)
        save_data = self.outputs.copy()
        if "iam_deployer_secret_access_key" in save_data:
            save_data["iam_deployer_secret_access_key"] = "[CONFIGURED IN AWS PROFILE 'terraform-user']"

        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_file.write_text(json.dumps(save_data, indent=2), encoding="utf-8")

        log_header("BOOTSTRAP COMPLETE - SUMMARY")
        log_success(f"Output Report saved to: {self.outputs_file.relative_to(self.repo_root)}")
        print(f"\n  • {Colors.BOLD}S3 Remote State Bucket{Colors.RESET} : {self.outputs['terraform_state_bucket']}")
        print(f"  • {Colors.BOLD}AWS Deployer Profile  {Colors.RESET} : terraform-user")
        print(f"  • {Colors.BOLD}GitHub Repository     {Colors.RESET} : {self.outputs['github_repository_url']}")
        print(f"  • {Colors.BOLD}GitHub OIDC Role ARN  {Colors.RESET} : {self.outputs['github_actions_role_arn']}")
        print(f"  • {Colors.BOLD}Route 53 Zone ID      {Colors.RESET} : {self.outputs['route53_zone_id']}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}Next Steps to Deploy Environments:{Colors.RESET}")
        print(f"  1. Deploy Backend DEV  : cd aws/infra/environments/dev/backend && terraform init && terraform apply")
        print(f"  2. Deploy Frontend DEV : cd aws/infra/environments/dev/frontend && terraform init && terraform apply\n")

    # --------------------------------------------------------------------------
    # Main Controller Flow
    # --------------------------------------------------------------------------
    def run(self):
        try:
            self.verify_prerequisites()
            self.collect_user_inputs()
            
            self.phase_1_bootstrap_s3()
            self.phase_2_update_provider_bucket()
            self.phase_3_deploy_iam_user()
            self.phase_4_configure_aws_profile()
            self.phase_5_provision_github_repo()
            self.phase_6_connect_local_clone()
            self.phase_7_deploy_oidc()
            self.phase_8_deploy_secrets_workflow()
            self.phase_9_deploy_dns_zone()
            self.phase_10_manual_registrar_pause()
            self.phase_11_deploy_certificates()
            
            self.save_outputs_and_summary()
        except KeyboardInterrupt:
            log_error("Bootstrap process interrupted by user.")
            sys.exit(1)
        except Exception as e:
            log_error(f"Bootstrap process failed: {e}")
            log_warn("Check the phase output above for troubleshooting details.")
            sys.exit(1)

if __name__ == "__main__":
    manager = BootstrapManager()
    manager.run()
