"""
Phase 6: Connect Local Clone to Provisioned GitHub Repository (git remote set-url & push).
"""

from pathlib import Path
from tools.utils.ui import log_phase, log_info, log_success, log_warn
from tools.utils.process import run_cmd

def run_phase_6(repo_root: Path, config: dict, outputs: dict):
    """Executes Phase 6: Updates remote origin URL with non-interactive PAT credentials and pushes codebase to main branch."""
    log_phase(6, 11, "Connect Local Clone to Provisioned GitHub Repository")
    
    owner = config["github_org_or_username"]
    token = config["github_token"]
    repo_full = outputs["github_repository_full_name"]

    # Non-interactive authenticated URL using owner and PAT token
    authenticated_git_url = f"https://{owner}:{token}@github.com/{repo_full}.git"
    sanitized_url = f"https://github.com/{repo_full}.git"

    log_info(f"Setting git remote origin to {sanitized_url}...")
    run_cmd(["git", "remote", "set-url", "origin", authenticated_git_url], cwd=repo_root)

    log_info("Pushing codebase to main branch...")
    try:
        # Initial push attempt
        run_cmd(["git", "push", "-u", "origin", "main"], cwd=repo_root)
        log_success("Codebase successfully pushed to new repository.")
    except Exception:
        log_warn("Initial push rejected (repository auto-initialized on GitHub). Fetching and integrating remote ref...")
        try:
            # Fetch remote and pull with rebase & allow-unrelated-histories
            run_cmd(["git", "fetch", "origin"], cwd=repo_root)
            run_cmd(["git", "pull", "origin", "main", "--rebase", "--allow-unrelated-histories"], cwd=repo_root)
            run_cmd(["git", "push", "-u", "origin", "main"], cwd=repo_root)
            log_success("Codebase successfully integrated and pushed to main branch.")
        except Exception:
            log_warn("Rebase returned conflict; forcing push to overwrite auto-initialized remote files...")
            # If stuck in rebase due to conflict, abort rebase and force push
            run_cmd(["git", "rebase", "--abort"], cwd=repo_root, check=False)
            run_cmd(["git", "push", "-u", "origin", "HEAD:refs/heads/main", "--force"], cwd=repo_root)
            log_success("Codebase successfully forced to main branch on GitHub.")

