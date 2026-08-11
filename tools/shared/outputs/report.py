"""
Output reporting module for writing JSON report files and displaying execution summary.
"""

import json
import time
from pathlib import Path
from tools.shared.ui.logger import Colors, log_header, log_success

def save_outputs_and_summary(repo_root: Path, outputs: dict, tool_name: str = "bootstrap"):
    """Saves output data to outputs/<tool_name>/outputs.json and displays final summary."""
    output_dir = repo_root / "outputs" / tool_name
    outputs_file = output_dir / "outputs.json"

    outputs["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    save_data = outputs.copy()
    if "iam_deployer_secret_access_key" in save_data and save_data["iam_deployer_secret_access_key"]:
        save_data["iam_deployer_secret_access_key"] = "[CONFIGURED IN AWS PROFILE 'terraform-user']"

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs_file.write_text(json.dumps(save_data, indent=2), encoding="utf-8")

    log_header(f"{tool_name.upper()} COMPLETE - SUMMARY")
    log_success(f"Output Report saved to: {outputs_file.relative_to(repo_root)}")
    
    if "terraform_state_bucket" in outputs and outputs["terraform_state_bucket"]:
        print(f"\n  • {Colors.BOLD}S3 Remote State Bucket{Colors.RESET} : {outputs['terraform_state_bucket']}")
        print(f"  • {Colors.BOLD}AWS Deployer Profile  {Colors.RESET} : terraform-user")
        print(f"  • {Colors.BOLD}GitHub Repository     {Colors.RESET} : {outputs.get('github_repository_url', 'N/A')}")
        print(f"  • {Colors.BOLD}GitHub OIDC Role ARN  {Colors.RESET} : {outputs.get('github_actions_role_arn', 'N/A')}")
        print(f"  • {Colors.BOLD}Route 53 Zone ID      {Colors.RESET} : {outputs.get('route53_zone_id', 'N/A')}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}Next Steps to Deploy Environments:{Colors.RESET}")
        print(f"  1. Deploy Backend DEV  : cd aws/infra/environments/dev/backend && terraform init && terraform apply")
        print(f"  2. Deploy Frontend DEV : cd aws/infra/environments/dev/frontend && terraform init && terraform apply\n")
