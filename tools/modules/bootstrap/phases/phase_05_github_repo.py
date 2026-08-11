"""
Phase 5: Provision GitHub Repository (pre-infra/github/repository).
"""

from pathlib import Path
from tools.shared.ui import log_phase, log_info, log_success
from tools.shared.utils import run_cmd

def run_phase_5(repo_root: Path, config: dict, outputs: dict):
    """Executes Phase 5: Provisions target GitHub repository via Terraform."""
    log_phase(5, 11, "Provision GitHub Repository (pre-infra/github/repository)")
    target_dir = repo_root / "aws/pre-infra/github/repository"

    log_info("Initializing Terraform...")
    run_cmd(["terraform", "init"], cwd=target_dir)

    log_info("Applying GitHub Repository resource...")
    tf_vars = [
        f"-var=github_token={config['github_token']}",
        f"-var=github_org_or_username={config['github_org_or_username']}",
        f"-var=github_repo_name={config['github_repo_name']}",
        f"-var=github_repo_visibility={config['github_repo_visibility']}"
    ]

    run_cmd(["terraform", "apply", "-auto-approve"] + tf_vars, cwd=target_dir)

    res_url = run_cmd(["terraform", "output", "-raw", "repository_html_url"], cwd=target_dir)
    res_full = run_cmd(["terraform", "output", "-raw", "repository_full_name"], cwd=target_dir)

    outputs["github_repository_url"] = res_url.stdout.strip()
    outputs["github_repository_full_name"] = res_full.stdout.strip()
    log_success(f"GitHub Repository Ready: {outputs['github_repository_full_name']}")
