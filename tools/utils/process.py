"""
Process execution and repository path utilities.
"""

import os
import subprocess
from pathlib import Path
from tools.utils.ui import Colors, log_error

def find_repo_root() -> Path:
    """Finds repository root directory."""
    current = Path.cwd().resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "aws").exists():
            return parent
    return current

def run_cmd(cmd, cwd=None, env=None, capture_output=True, check=True):
    """Utility wrapper for subprocess execution."""
    try:
        res = subprocess.run(
            cmd,
            cwd=cwd,
            env=env or os.environ.copy(),
            capture_output=capture_output,
            text=True,
            check=check
        )
        return res
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        if e.stdout:
            print(f"{Colors.YELLOW}STDOUT:\n{e.stdout}{Colors.RESET}")
        if e.stderr:
            print(f"{Colors.RED}STDERR:\n{e.stderr}{Colors.RESET}")
        raise e
