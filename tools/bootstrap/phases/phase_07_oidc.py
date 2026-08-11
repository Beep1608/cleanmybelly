"""
Phase 7: Deploy GitHub OIDC Trust (pre-infra/github/oidc).
"""

from pathlib import Path
from tools.shared.ui import log_phase, log_info, log_success
from tools.shared.utils import run_cmd

def run_phase_7(repo_root: Path, outputs: dict):
    """Executes Phase 7: Provisions AWS IAM OIDC trust for GitHub Actions."""
    log_phase(7, 11, "Deploy GitHub OIDC Trust (pre-infra/github/oidc)")
    target_dir = repo_root / "aws/pre-infra/github/oidc"

    log_info("Initializing Terraform...")
    run_cmd(["terraform", "init"], cwd=target_dir)

    log_info("Applying OIDC trust configuration...")
    bucket_var = f"-var=terraform_state_bucket_name={outputs['terraform_state_bucket']}"
    run_cmd(["terraform", "apply", "-auto-approve", bucket_var], cwd=target_dir)

    res_role = run_cmd(["terraform", "output", "-raw", "github_actions_role_arn"], cwd=target_dir)
    outputs["github_actions_role_arn"] = res_role.stdout.strip()
    log_success(f"OIDC Role ARN: {outputs['github_actions_role_arn']}")
