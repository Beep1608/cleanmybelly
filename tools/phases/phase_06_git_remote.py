"""
Phase 6: Connect Local Clone to Provisioned GitHub Repository (git remote set-url & push).
"""

from pathlib import Path
from tools.utils.ui import log_phase, log_info, log_success, log_warn
from tools.utils.process import run_cmd

def run_phase_6(repo_root: Path, outputs: dict):
    """Executes Phase 6: Updates remote origin URL and pushes codebase to main branch."""
    log_phase(6, 11, "Connect Local Clone to Provisioned GitHub Repository")
    repo_url = outputs["github_repository_url"]
    git_remote_url = f"{repo_url}.git"

    log_info(f"Setting git remote origin to {git_remote_url}...")
    run_cmd(["git", "remote", "set-url", "origin", git_remote_url], cwd=repo_root)

    log_info("Pushing codebase to main branch...")
    try:
        run_cmd(["git", "push", "-u", "origin", "main"], cwd=repo_root)
        log_success("Codebase successfully pushed to new repository.")
    except Exception:
        log_warn("Initial push to main returned a non-zero code. Retrying with explicit ref...")
        run_cmd(["git", "push", "-u", "origin", "HEAD:refs/heads/main"], cwd=repo_root)
        log_success("Codebase pushed to main branch.")
