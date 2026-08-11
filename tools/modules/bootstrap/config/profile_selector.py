"""
AWS Profile Selector Module.
Lists available AWS CLI profiles and allows interactive selection.
"""

import os
from tools.shared.ui import Colors, log_info, log_success, log_warn, log_error
from tools.shared.utils import run_cmd

def select_aws_profile() -> str:
    """
    Lists available AWS CLI profiles via 'aws configure list-profiles'
    and prompts the user to select an active profile.
    """
    print(f"\n{Colors.BOLD}{Colors.CYAN}--- AWS Profile Selection ---{Colors.RESET}\n")
    log_info("Phase 0 bootstrapping requires an AWS Administrator identity (Root or Admin IAM user/role).")

    profiles = []
    try:
        res = run_cmd(["aws", "configure", "list-profiles"], check=False)
        if res.returncode == 0 and res.stdout:
            profiles = [p.strip() for p in res.stdout.splitlines() if p.strip()]
    except Exception:
        pass

    if not profiles:
        profiles = ["default"]

    current_profile = os.environ.get("AWS_PROFILE", "default")
    
    print(f"  {Colors.BOLD}Available AWS CLI Profiles:{Colors.RESET}")
    for idx, profile_name in enumerate(profiles, 1):
        is_current = " (active)" if profile_name == current_profile else ""
        print(f"    {idx}. {profile_name}{is_current}")

    default_choice = 1
    if current_profile in profiles:
        default_choice = profiles.index(current_profile) + 1

    selected_profile = current_profile
    while True:
        choice_input = input(f"\n{Colors.BOLD}Select AWS Profile [1-{len(profiles)}] (default: {default_choice}): {Colors.RESET}").strip()
        if not choice_input:
            selected_profile = profiles[default_choice - 1]
            break
        if choice_input.isdigit():
            val = int(choice_input)
            if 1 <= val <= len(profiles):
                selected_profile = profiles[val - 1]
                break
        log_error(f"Invalid selection. Please enter a number between 1 and {len(profiles)}.")

    # Export selected profile for all subsequent subprocess executions
    os.environ["AWS_PROFILE"] = selected_profile
    log_success(f"Active AWS Profile set to: '{selected_profile}' (export AWS_PROFILE={selected_profile})")
    return selected_profile
