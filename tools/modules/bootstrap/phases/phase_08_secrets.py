"""
Phase 8: Deploy Secrets & Workflow Publishing (pre-infra/github/secrets-workflow).
"""

from pathlib import Path
from tools.shared.ui import log_phase, log_info, log_success
from tools.shared.utils import run_cmd

def run_phase_8(repo_root: Path, config: dict, outputs: dict):
    """Executes Phase 8: Injects secrets and publishes workflow files."""
    log_phase(8, 11, "Deploy Secrets & Workflow Publishing (pre-infra/github/secrets-workflow)")
    target_dir = repo_root / "aws/pre-infra/github/secrets-workflow"

    log_info("Initializing Terraform...")
    run_cmd(["terraform", "init", "-reconfigure"], cwd=target_dir)

    log_info("Applying Secrets and Workflow Publishing...")
    tf_vars = [
        f"-var=github_token={config['github_token']}",
        f"-var=terraform_state_bucket_name={outputs['terraform_state_bucket']}",
        f"-var=github_org_or_username={config['github_org_or_username']}"
    ]

    run_cmd(["terraform", "apply", "-auto-approve"] + tf_vars, cwd=target_dir)
    log_success("GitHub Secrets and deployment workflow published successfully.")
