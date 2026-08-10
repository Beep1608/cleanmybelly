"""
Prerequisite validation module for checking Python, Terraform, AWS CLI, and Git system tools.
"""

import sys
import shutil
from pathlib import Path
from tools.utils.ui import log_header, log_success, log_info, log_error
from tools.utils.process import run_cmd

def verify_prerequisites(repo_root: Path):
    """Verifies system CLI tool dependencies before running the bootstrap workflow."""
    log_header("cleanmybelly Bootstrap CLI - Prerequisites Check")
    log_info(f"Repository Root: {repo_root}")

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

    # 4. Check Git
    if not shutil.which("git"):
        log_error("Git CLI not found in PATH.")
        sys.exit(1)
    log_success("Git CLI verified")

    # 5. Verify inside Git repository
    try:
        run_cmd(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root)
        log_success("Git repository verified")
    except Exception:
        log_error(f"{repo_root} is not a valid Git repository.")
        sys.exit(1)
