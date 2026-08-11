"""
Execution phase modules for the bootstrap workflow.
"""

from tools.bootstrap.phases.phase_01_s3 import run_phase_1
from tools.bootstrap.phases.phase_02_find_replace import run_phase_2
from tools.bootstrap.phases.phase_03_iam_user import run_phase_3
from tools.bootstrap.phases.phase_04_aws_profile import run_phase_4
from tools.bootstrap.phases.phase_05_github_repo import run_phase_5
from tools.bootstrap.phases.phase_06_git_remote import run_phase_6
from tools.bootstrap.phases.phase_07_oidc import run_phase_7
from tools.bootstrap.phases.phase_08_secrets import run_phase_8
from tools.bootstrap.phases.phase_09_dns_zone import run_phase_9
from tools.bootstrap.phases.phase_10_registrar import run_phase_10
from tools.bootstrap.phases.phase_11_certs import run_phase_11

__all__ = [
    "run_phase_1", "run_phase_2", "run_phase_3", "run_phase_4",
    "run_phase_5", "run_phase_6", "run_phase_7", "run_phase_8",
    "run_phase_9", "run_phase_10", "run_phase_11"
]
