"""
Phase 4: Configure Local AWS CLI Profile 'terraform-user'.
"""

from tools.shared.ui import log_phase, log_success
from tools.shared.utils import run_cmd

def run_phase_4(config: dict, outputs: dict):
    """Executes Phase 4: Configures AWS CLI profile 'terraform-user'."""
    log_phase(4, 11, "Configure Local AWS Profile 'terraform-user'")
    profile = "terraform-user"
    key_id = outputs["iam_deployer_access_key_id"]
    secret_key = outputs["iam_deployer_secret_access_key"]
    region = config["aws_region"]

    run_cmd(["aws", "configure", "set", "aws_access_key_id", key_id, "--profile", profile])
    run_cmd(["aws", "configure", "set", "aws_secret_access_key", secret_key, "--profile", profile])
    run_cmd(["aws", "configure", "set", "region", region, "--profile", profile])

    log_success(f"AWS CLI profile '{profile}' configured successfully.")
