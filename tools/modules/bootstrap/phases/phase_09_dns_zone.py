"""
Phase 9: Deploy Route 53 Hosted Zone (infra/shared/networking/dns-zone).
"""

import json
from pathlib import Path
from tools.shared.ui import log_phase, log_info, log_success
from tools.shared.utils import run_cmd

def run_phase_9(repo_root: Path, config: dict, outputs: dict):
    """Executes Phase 9: Provisions Route 53 primary hosted zone."""
    log_phase(9, 11, "Deploy Route 53 Hosted Zone (infra/shared/networking/dns-zone)")
    target_dir = repo_root / "aws/infra/shared/networking/dns-zone"

    log_info("Initializing Terraform...")
    run_cmd(["terraform", "init", "-reconfigure"], cwd=target_dir)

    log_info("Applying Route 53 DNS Zone...")
    domain_var = f"-var=hosted_zone_name={config['domain_name']}"
    run_cmd(["terraform", "apply", "-auto-approve", domain_var], cwd=target_dir)

    res_zone = run_cmd(["terraform", "output", "-raw", "hosted_zone_id"], cwd=target_dir)
    res_ns = run_cmd(["terraform", "output", "-json", "name_servers"], cwd=target_dir)

    outputs["route53_zone_id"] = res_zone.stdout.strip()
    outputs["route53_name_servers"] = json.loads(res_ns.stdout)

    log_success(f"Route 53 Zone ID: {outputs['route53_zone_id']}")
