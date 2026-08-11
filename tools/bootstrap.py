#!/usr/bin/env python3
"""
cleanmybelly Bootstrap CLI Tool - Main Orchestrator

Automated Python CLI tool for end-to-end infrastructure bootstrapping on AWS & GitHub.
Refactored into dedicated modules under tools/ for single responsibility.

Usage:
    python3 tools/bootstrap.py
    python3 tools/bootstrap.py --skip-permission-check
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.utils.process import find_repo_root, run_cmd
from tools.utils.ui import Colors, log_error, log_warn, log_success, log_info
from tools.validators.prerequisites import verify_prerequisites
from tools.validators.aws_permissions import verify_aws_permissions
from tools.config.profile_selector import select_aws_profile
from tools.config.inputs import collect_user_inputs
from tools.phases.phase_01_s3 import run_phase_1
from tools.phases.phase_02_find_replace import run_phase_2
from tools.phases.phase_03_iam_user import run_phase_3
from tools.phases.phase_04_aws_profile import run_phase_4
from tools.phases.phase_05_github_repo import run_phase_5
from tools.phases.phase_06_git_remote import run_phase_6
from tools.phases.phase_07_oidc import run_phase_7
from tools.phases.phase_08_secrets import run_phase_8
from tools.phases.phase_09_dns_zone import run_phase_9
from tools.phases.phase_10_registrar import run_phase_10
from tools.phases.phase_11_certs import run_phase_11
from tools.outputs.tracker import ExecutionTracker
from tools.outputs.report import save_outputs_and_summary

class BootstrapOrchestrator:
    """Main orchestrator executing all validation, configuration, and setup phases."""
    def __init__(self, skip_permission_check: bool = False):
        self.repo_root = find_repo_root()
        self.skip_permission_check = skip_permission_check
        self.active_profile = "default"
        self.config = {}
        self.outputs = {
            "timestamp": "",
            "terraform_state_bucket": "",
            "iam_deployer_user": "terraform-deployer",
            "iam_deployer_access_key_id": "",
            "github_repository_url": "",
            "github_repository_full_name": "",
            "github_actions_role_arn": "",
            "route53_zone_id": "",
            "route53_name_servers": [],
            "acm_certificates": {}
        }
        self.tracker = None

    def check_aws_identity_and_permissions(self):
        """Verifies active AWS credentials identity for selected profile and tests administrative permissions strictly."""
        caller_arn = ""
        try:
            res = run_cmd(["aws", "sts", "get-caller-identity"])
            identity = json.loads(res.stdout)
            caller_arn = identity.get("Arn", "")
            log_success(f"AWS Active Identity ({self.active_profile}): {caller_arn}")
            log_info(f"AWS Account ID: {identity.get('Account')}")
        except Exception:
            log_error(f"AWS Authentication check failed for profile '{self.active_profile}'.")
            print(f"\n  {Colors.BOLD}{Colors.YELLOW}Suggested Resolution:{Colors.RESET}")
            print(f"    • If your session expired (AWS SSO): run {Colors.BOLD}aws sso login --profile {self.active_profile}{Colors.RESET} or {Colors.BOLD}aws login{Colors.RESET}")
            print(f"    • If configuring a new AWS profile: run {Colors.BOLD}aws configure --profile {self.active_profile}{Colors.RESET}\n")
            sys.exit(1)

        # Strictly verify active AWS administrative permissions
        verify_aws_permissions(caller_arn, skip_permission_check=self.skip_permission_check)

    def run(self):
        """Executes the full bootstrap lifecycle sequentially."""
        try:
            # 1. Verify system dependencies
            verify_prerequisites(self.repo_root)

            # 2. Interactive AWS Profile Selector
            self.active_profile = select_aws_profile()

            # 3. Check Identity & Permissions for selected profile
            self.check_aws_identity_and_permissions()

            # 4. Collect user configuration inputs
            self.config = collect_user_inputs(self.repo_root)

            # 5. Initialize step-by-step execution tracker
            self.tracker = ExecutionTracker(self.repo_root)

            # Phase 1: S3 State Bucket
            self.tracker.start_phase(1)
            run_phase_1(self.repo_root, self.config, self.outputs)
            self.tracker.complete_phase(1, self.outputs)

            # Phase 2: Global Provider Find & Replace
            self.tracker.start_phase(2)
            run_phase_2(self.repo_root, self.outputs)
            self.tracker.complete_phase(2, self.outputs)

            # Phase 3: IAM Deployer User
            self.tracker.start_phase(3)
            run_phase_3(self.repo_root, self.outputs)
            self.tracker.complete_phase(3, self.outputs)

            # Phase 4: AWS CLI Profile Setup
            self.tracker.start_phase(4)
            run_phase_4(self.config, self.outputs)
            self.tracker.complete_phase(4, self.outputs)

            # Phase 5: GitHub Repository Provisioning
            self.tracker.start_phase(5)
            run_phase_5(self.repo_root, self.config, self.outputs)
            self.tracker.complete_phase(5, self.outputs)

            # Phase 6: Connect Local Clone & Push
            self.tracker.start_phase(6)
            run_phase_6(self.repo_root, self.config, self.outputs)
            self.tracker.complete_phase(6, self.outputs)

            # Phase 7: GitHub OIDC Trust Setup
            self.tracker.start_phase(7)
            run_phase_7(self.repo_root, self.outputs)
            self.tracker.complete_phase(7, self.outputs)

            # Phase 8: Secrets & Workflow Publishing
            self.tracker.start_phase(8)
            run_phase_8(self.repo_root, self.config, self.outputs)
            self.tracker.complete_phase(8, self.outputs)

            # Phase 9: Route 53 DNS Hosted Zone
            self.tracker.start_phase(9)
            run_phase_9(self.repo_root, self.config, self.outputs)
            self.tracker.complete_phase(9, self.outputs)

            # Phase 10: Registrar Setup & Manual Pause
            self.tracker.start_phase(10)
            run_phase_10(self.config, self.outputs)
            self.tracker.complete_phase(10, self.outputs)

            # Phase 11: ACM SSL Certificates
            self.tracker.start_phase(11)
            run_phase_11(self.repo_root, self.config, self.outputs)
            self.tracker.complete_phase(11, self.outputs)

            # Mark all as complete
            self.tracker.complete_all()
            save_outputs_and_summary(self.repo_root, self.outputs)
        except KeyboardInterrupt:
            if self.tracker and self.tracker.status_data.get("current_phase"):
                self.tracker.fail_phase(self.tracker.status_data["current_phase"], "Interrupted by user")
            log_error("Bootstrap process interrupted by user.")
            sys.exit(1)
        except Exception as e:
            if self.tracker and self.tracker.status_data.get("current_phase"):
                self.tracker.fail_phase(self.tracker.status_data["current_phase"], str(e))
            log_error(f"Bootstrap process failed: {e}")
            log_warn("Check tools/bootstrap_status.log and tools/bootstrap_status.json for detailed status.")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="cleanmybelly Bootstrap CLI Tool - End-to-end AWS & GitHub infrastructure setup."
    )
    parser.add_argument(
        "--skip-permission-check",
        action="store_true",
        help="Bypass strict IAM permission simulation check if you are certain your identity has required AWS permissions."
    )
    args = parser.parse_args()

    orchestrator = BootstrapOrchestrator(skip_permission_check=args.skip_permission_check)
    orchestrator.run()

if __name__ == "__main__":
    main()
