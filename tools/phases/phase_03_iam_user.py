"""
Phase 3: Deploy IAM Deployer User (pre-infra/iam-deployer).
"""

from pathlib import Path
from tools.utils.ui import log_phase, log_info, log_success
from tools.utils.process import run_cmd

def run_phase_3(repo_root: Path, outputs: dict):
    """Executes Phase 3: Deploys IAM deployer user and credentials."""
    log_phase(3, 11, "Deploy IAM Deployer User (pre-infra/iam-deployer)")
    target_dir = repo_root / "aws/pre-infra/iam-deployer"

    log_info("Initializing Terraform...")
    run_cmd(["terraform", "init"], cwd=target_dir)

    log_info("Applying IAM deployer user configuration...")
    run_cmd(["terraform", "apply", "-auto-approve"], cwd=target_dir)

    res_id = run_cmd(["terraform", "output", "-raw", "deployer_access_key_id"], cwd=target_dir)
    res_secret = run_cmd(["terraform", "output", "-raw", "deployer_secret_access_key"], cwd=target_dir)

    outputs["iam_deployer_access_key_id"] = res_id.stdout.strip()
    outputs["iam_deployer_secret_access_key"] = res_secret.stdout.strip()
    log_success("IAM Deployer user and credentials generated.")
