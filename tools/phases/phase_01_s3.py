"""
Phase 1: Bootstrap S3 Remote State Bucket (pre-infra/bootstrap).
"""

from pathlib import Path
from tools.utils.ui import log_phase, log_info, log_success
from tools.utils.process import run_cmd

def run_phase_1(repo_root: Path, outputs: dict):
    """Executes Phase 1: Provisions S3 Remote State bucket."""
    log_phase(1, 11, "Bootstrap S3 Remote State Bucket (pre-infra/bootstrap)")
    target_dir = repo_root / "aws/pre-infra/bootstrap"
    
    log_info("Initializing Terraform in aws/pre-infra/bootstrap...")
    run_cmd(["terraform", "init"], cwd=target_dir)

    log_info("Applying Terraform configuration...")
    run_cmd(["terraform", "apply", "-auto-approve"], cwd=target_dir)

    res = run_cmd(["terraform", "output", "-raw", "terraform_state_bucket_name"], cwd=target_dir)
    bucket_name = res.stdout.strip()
    outputs["terraform_state_bucket"] = bucket_name
    log_success(f"S3 Remote State Bucket Created: {bucket_name}")
