"""
Phase 10: Manual Registrar Setup Pause & DNS Propagation Verification.
"""

from tools.shared.ui import Colors, log_phase, log_info, log_success, log_warn
from tools.shared.utils import run_cmd

def run_phase_10(config: dict, outputs: dict):
    """Executes Phase 10: Pauses for manual Name Server configuration at domain registrar."""
    log_phase(10, 11, "Manual Domain Registrar Setup & Propagation Verification")
    name_servers = outputs["route53_name_servers"]
    domain = config["domain_name"]

    print(f"\n{Colors.BOLD}{Colors.YELLOW}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}║  ⚠ ACTION REQUIRED: CONFIGURE DOMAIN REGISTRAR NAME SERVERS                  ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
    print(f"{Colors.YELLOW}║ Log into your domain registrar (e.g. Namecheap, GoDaddy, Route 53)           ║{Colors.RESET}")
    print(f"{Colors.YELLOW}║ for domain '{Colors.BOLD}{domain}{Colors.RESET}{Colors.YELLOW}' and update Custom DNS to these 4 Name Servers:  ║{Colors.RESET}")
    print(f"{Colors.YELLOW}║                                                                              ║{Colors.RESET}")
    for i, ns in enumerate(name_servers, 1):
        print(f"{Colors.YELLOW}║   {i}. {Colors.BOLD}{ns.ljust(68)}{Colors.RESET}{Colors.YELLOW} ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

    input(f"{Colors.BOLD}{Colors.CYAN}Press [ENTER] once you have updated your Name Servers at your registrar...{Colors.RESET}")

    log_info(f"Verifying DNS propagation for {domain}...")
    try:
        res = run_cmd(["dig", "+short", domain, "NS"], check=False)
        if res.stdout:
            log_success("DNS records retrieved via dig:")
            print(f"    {res.stdout.strip()}")
        else:
            log_warn("DNS propagation is still in progress. Continuing setup...")
    except Exception:
        log_warn("Unable to execute 'dig'. Continuing with certificate issuance...")
