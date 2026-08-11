"""
UI formatting and logging utilities for the cleanmybelly CLI tools.
"""

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_header(title: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║  {title.ljust(75)} ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")

def log_phase(phase_num: int, total_phases: int, title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}[PHASE {phase_num}/{total_phases}] {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'─' * 70}{Colors.RESET}")

def log_success(msg: str):
    print(f"  {Colors.GREEN}✓ {msg}{Colors.RESET}")

def log_info(msg: str):
    print(f"  {Colors.CYAN}ℹ {msg}{Colors.RESET}")

def log_warn(msg: str):
    print(f"  {Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def log_error(msg: str):
    print(f"  {Colors.RED}✗ {msg}{Colors.RESET}")
