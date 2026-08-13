"""
Scope mapping module for env-sync.
Defines the static association between parent directories and their respective .env files.
"""

import os
from typing import List, Dict, Tuple


def get_repo_root() -> str:
    """Returns the absolute path to the repository root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # modules/env_sync -> tools -> repo_root
    return os.path.abspath(os.path.join(current_dir, "../../../"))


SCOPE_MAP: List[Dict[str, str]] = [
    {
        "scope_name": "pre-infra",
        "parent_dir": "aws/pre-infra",
        "env_file": "environments/global/.env.pre-infra",
        "example_file": "environments/global/.env.pre-infra.example",
    },
    {
        "scope_name": "shared",
        "parent_dir": "aws/infra/shared",
        "env_file": "environments/global/.env.shared",
        "example_file": "environments/global/.env.shared.example",
    },
    {
        "scope_name": "dev",
        "parent_dir": "aws/infra/environments/dev",
        "env_file": "environments/dev/.env.dev",
        "example_file": "environments/dev/.env.dev.example",
    },
    {
        "scope_name": "prod",
        "parent_dir": "aws/infra/environments/prod",
        "env_file": "environments/prod/.env.prod",
        "example_file": "environments/prod/.env.prod.example",
    },
]


def validate_env_files_exist(repo_root: str) -> Tuple[bool, List[Tuple[str, str]]]:
    """
    Checks whether all required .env files exist in the repository.
    Returns (is_valid, list_of_missing_tuples_of_(env_rel_path, example_rel_path)).
    """
    missing = []
    for entry in SCOPE_MAP:
        env_abs_path = os.path.join(repo_root, entry["env_file"])
        if not os.path.exists(env_abs_path):
            missing.append((entry["env_file"], entry["example_file"]))
    
    return len(missing) == 0, missing
