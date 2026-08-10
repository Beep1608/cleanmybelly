"""
Phase 11: Deploy ACM SSL Certificates (infra/shared/networking/certificates).
"""

from pathlib import Path
from tools.utils.ui import log_phase, log_info, log_success
from tools.utils.process import run_cmd

def run_phase_11(repo_root: Path, config: dict, outputs: dict):
    """Executes Phase 11: Requests and validates ACM SSL certificates via Route 53."""
    log_phase(11, 11, "Deploy ACM SSL Certificates (infra/shared/networking/certificates)")
    target_dir = repo_root / "aws/infra/shared/networking/certificates"

    log_info("Initializing Terraform...")
    run_cmd(["terraform", "init"], cwd=target_dir)

    log_info("Applying ACM Certificates and Route 53 DNS validation...")
    domain_var = f"-var=hosted_zone_name={config['domain_name']}"
    run_cmd(["terraform", "apply", "-auto-approve", domain_var], cwd=target_dir)

    certs = {}
    for output_key in ["dev_frontend_cert_arn", "dev_backend_cert_arn", "prod_frontend_cert_arn", "prod_backend_cert_arn"]:
        try:
            res = run_cmd(["terraform", "output", "-raw", output_key], cwd=target_dir, check=False)
            if res.stdout:
                certs[output_key] = res.stdout.strip()
        except Exception:
            pass

    outputs["acm_certificates"] = certs
    log_success("ACM SSL Certificates issued and validated successfully.")
