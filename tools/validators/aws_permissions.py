"""
AWS Identity and Administrative Permissions Validator.
Strictly verifies that the active AWS identity possesses required Phase 0 permissions
with support for --skip-permission-check bypass.
"""

import sys
import json
from tools.utils.ui import Colors, log_success, log_info, log_warn, log_error
from tools.utils.process import run_cmd

def verify_aws_permissions(caller_arn: str, skip_permission_check: bool = False):
    """
    Verifies active AWS identity and administrative permissions for Phase 0 bootstrapping.
    Fails if identity lacks required permissions, unless --skip-permission-check is passed.
    """
    log_info("Phase 0 bootstrapping requires an AWS Administrator identity (Root or Admin IAM user/role).")

    # 1. Bypass check if user explicitly passed --skip-permission-check
    if skip_permission_check:
        log_warn("IAM permission simulation check bypassed via --skip-permission-check flag.")
        log_success(f"Proceeding with active AWS Identity: {caller_arn}")
        return

    # 2. AWS Account Root User has implicit full administrative access.
    if caller_arn.endswith(":root"):
        log_warn("AWS Root Account identity detected (Root account usage is not recommended for daily operations).")
        log_success("Root account verified (implicit full administrative access).")
        return

    # 3. Required Phase 0 administrative actions
    required_actions = [
        "s3:CreateBucket",
        "iam:CreateUser",
        "iam:CreateRole",
        "route53:CreateHostedZone"
    ]
    
    log_info("Programmatically testing AWS administrative permissions...")
    failed_actions = []
    
    for action in required_actions:
        cmd = [
            "aws", "iam", "simulate-principal-policy",
            "--policy-source-arn", caller_arn,
            "--action-names", action
        ]
        res = run_cmd(cmd, check=False)
        if res.returncode == 0 and res.stdout:
            try:
                data = json.loads(res.stdout)
                eval_results = data.get("EvaluationResults", [])
                if eval_results:
                    decision = eval_results[0].get("EvalDecision", "unknown")
                    if decision == "allowed":
                        log_success(f"Permission verified: {action} [{decision}]")
                    else:
                        failed_actions.append(f"{action} [{decision}]")
                        log_error(f"Permission check failed: {action} [{decision}]")
                else:
                    failed_actions.append(f"{action} [empty evaluation]")
            except Exception as e:
                failed_actions.append(f"{action} [parse error: {e}]")
        else:
            stderr_msg = res.stderr.strip() if res.stderr else "AccessDenied/Restricted"
            failed_actions.append(f"{action} [{stderr_msg}]")
            log_error(f"Simulation restricted for {action}: {stderr_msg}")

    # Strict Enforcement
    if failed_actions:
        print(f"\n{Colors.BOLD}{Colors.RED}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}║ ✗ STRICT PERMISSION CHECK FAILED                                             ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        print(f"{Colors.RED}║ Identity: {caller_arn[:62].ljust(62)} ║{Colors.RESET}")
        print(f"{Colors.RED}║ Phase 0 bootstrapping requires an active AWS Administrator identity.          ║{Colors.RESET}")
        print(f"{Colors.RED}║ Some permissions simulation checks failed or were restricted.                ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")
        
        print(f"  {Colors.BOLD}{Colors.YELLOW}Suggested Resolution:{Colors.RESET}")
        print(f"    1. Switch to an AWS Administrator account/profile with full access.")
        print(f"    2. If you are CERTAIN your active identity has all required permissions")
        print(f"       (even if 'iam:SimulatePrincipalPolicy' is restricted on your account),")
        print(f"       bypass this check by running:")
        print(f"       {Colors.BOLD}python3 tools/bootstrap.py --skip-permission-check{Colors.RESET}\n")
        sys.exit(1)

    log_success("All required AWS administrative permissions verified programmatically.")
