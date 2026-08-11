"""
Module for collecting interactive configuration inputs from the user.
"""

from pathlib import Path
from tools.shared.ui import Colors, log_error
from tools.shared.utils import run_cmd

def collect_user_inputs(repo_root: Path) -> dict:
    """Collects interactive configuration parameters from the user."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Configuration Inputs ---{Colors.RESET}\n")

    config = {
        "github_token": "",
        "github_org_or_username": "",
        "github_repo_name": "",
        "github_repo_visibility": "public",
        "domain_name": "",
        "aws_region": "us-east-1"
    }

    # 1. GitHub Token
    while True:
        token = input(f"{Colors.BOLD}Enter your GitHub Personal Access Token (PAT): {Colors.RESET}").strip()
        if token:
            config["github_token"] = token
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
    config["github_org_or_username"] = user_input if user_input else default_user

    # 3. GitHub Repo Name
    default_repo = repo_root.name
    repo_input = input(f"{Colors.BOLD}Enter target GitHub repository name [{default_repo}]: {Colors.RESET}").strip()
    config["github_repo_name"] = repo_input if repo_input else default_repo

    # 4. Repo Visibility
    vis_input = input(f"{Colors.BOLD}Enter repository visibility (public/private) [public]: {Colors.RESET}").strip().lower()
    config["github_repo_visibility"] = vis_input if vis_input in ["public", "private"] else "public"

    # 5. Domain Name
    while True:
        domain = input(f"{Colors.BOLD}Enter your root domain name (e.g. cleanmybelly.com): {Colors.RESET}").strip()
        if domain and "." in domain:
            config["domain_name"] = domain
            break
        log_error("Valid domain name is required (e.g. example.com).")

    # 6. AWS Region
    region_input = input(f"{Colors.BOLD}Enter AWS Region [us-east-1]: {Colors.RESET}").strip()
    config["aws_region"] = region_input if region_input else "us-east-1"

    print(f"\n{Colors.GREEN}✓ Configuration confirmed:{Colors.RESET}")
    print(f"  • GitHub Owner : {config['github_org_or_username']}")
    print(f"  • GitHub Repo  : {config['github_repo_name']} ({config['github_repo_visibility']})")
    print(f"  • Root Domain  : {config['domain_name']}")
    print(f"  • AWS Region   : {config['aws_region']}")

    return config
