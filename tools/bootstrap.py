#!/usr/bin/env python3
"""
cleanmybelly Bootstrap CLI Tool - Main Orchestrator

Automated Python CLI tool for end-to-end infrastructure bootstrapping on AWS & GitHub.
Refactored into dedicated modules under tools/ for single responsibility.

Usage:
    python3 tools/bootstrap.py
"""

import sys
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.utils.process import find_repo_root
from tools.utils.ui import log_error, log_warn
from tools.validators.prerequisites import verify_prerequisites
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
from tools.outputs.report import save_outputs_and_summary

class BootstrapOrchestrator:
    """Main orchestrator executing all validation, configuration, and setup phases."""
    def __init__(self):
        self.repo_root = find_repo_root()
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

    def run(self):
        """Executes the full bootstrap lifecycle sequentially."""
        try:
            verify_prerequisites(self.repo_root)
            self.config = collect_user_inputs(self.repo_root)
            
            run_phase_1(self.repo_root, self.outputs)
            run_phase_2(self.repo_root, self.outputs)
            run_phase_3(self.repo_root, self.outputs)
            run_phase_4(self.config, self.outputs)
            run_phase_5(self.repo_root, self.config, self.outputs)
            run_phase_6(self.repo_root, self.outputs)
            run_phase_7(self.repo_root, self.outputs)
            run_phase_8(self.repo_root, self.config, self.outputs)
            run_phase_9(self.repo_root, self.config, self.outputs)
            run_phase_10(self.config, self.outputs)
            run_phase_11(self.repo_root, self.config, self.outputs)
            
            save_outputs_and_summary(self.repo_root, self.outputs)
        except KeyboardInterrupt:
            log_error("Bootstrap process interrupted by user.")
            sys.exit(1)
        except Exception as e:
            log_error(f"Bootstrap process failed: {e}")
            log_warn("Check the phase output above for troubleshooting details.")
            sys.exit(1)

if __name__ == "__main__":
    orchestrator = BootstrapOrchestrator()
    orchestrator.run()
