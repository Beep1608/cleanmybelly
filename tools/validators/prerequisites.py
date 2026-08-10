"""
Prerequisite validation module for checking Python, Terraform, AWS CLI, AWS identity, AWS permissions, and Git.
"""

import sys
import json
import shutil
from pathlib import Path
from tools.utils.ui import log_header, log_success, log_info, log_warn, log_error
from tools.utils.process import run_cmd

def verify_aws_permissions(caller_arn: str):
    """Programmatically tests active AWS permissions using iam simulate-principal-policy."""
    actions = [
        "s3:CreateBucket",
        "iam:CreateUser",
        "iam:CreateRole",
        "route53:CreateHostedZone"
    ]
    
    log_info("Programmatically testing AWS administrative permissions...")
    try:
        cmd = [
            "aws", "iam", "simulate-principal-policy",
            "--policy-source-arn", caller_arn,
            "--action-names"
        ] + actions
        
        res = run_cmd(cmd, check=False)
        if res.returncode == 0 and res.stdout:
            data = json.loads(res.stdout)
            eval_results = data.get("EvaluationResults", [])
            
            allowed_count = 0
            for eval_item in eval_results:
                action = eval_item.get("EvalActionName")
                decision = eval_item.get("EvalDecision")
                if decision == "allowed":
                    allowed_count += 1
                    log_success(f"Permission verified: {action} [allowed]")
                else:
                    log_warn(f"Permission check: {action} [{decision}]")
            
            if allowed_count == len(actions):
                log_success("All AWS administrative permissions verified programmatically.")
            else:
                log_warn("Some permissions simulation checks returned implicit/explicit deny.")
                log_warn("Ensure your active AWS user/role has AdministratorAccess for Phase 0 setup.")
        else:
            log_warn("Unable to simulate principal policy (iam:SimulatePrincipalPolicy may be restricted).")
            log_warn("Proceeding with identity ARN assumption...")
    except Exception as e:
        log_warn(f"AWS permissions simulation check skipped: {e}")

def verify_prerequisites(repo_root: Path):
    """Verifies all system dependencies and active permissions before starting the bootstrap workflow."""
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

    # 4. Check AWS Credentials & Active Identity
    caller_arn = ""
    try:
        res = run_cmd(["aws", "sts", "get-caller-identity"])
        identity = json.loads(res.stdout)
        caller_arn = identity.get("Arn", "")
        log_success(f"AWS Active Identity: {caller_arn}")
        log_info(f"AWS Account ID: {identity.get('Account')}")
    except Exception:
        log_error("No active AWS credentials found or identity check failed.")
        log_warn("Please run 'aws configure' or export AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY before running this tool.")
        sys.exit(1)

    # 5. Programmatically test active AWS administrative permissions
    if caller_arn:
        verify_aws_permissions(caller_arn)

    # 6. Check Git
    if not shutil.which("git"):
        log_error("Git CLI not found in PATH.")
        sys.exit(1)
    log_success("Git CLI verified")

    # 7. Verify inside Git repository
    try:
        run_cmd(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root)
        log_success("Git repository verified")
    except Exception:
        log_error(f"{repo_root} is not a valid Git repository.")
        sys.exit(1)
