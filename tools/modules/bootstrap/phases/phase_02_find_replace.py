"""
Phase 2: Synchronize Environment Variables and Generate Backend Configurations via env-sync.
"""

import re
from pathlib import Path
from tools.shared.ui import log_phase, log_info, log_success, log_error
from tools.modules.env_sync import synchronize_all


def _update_env_file_backend_bucket(env_file_path: Path, bucket_name: str):
    """Updates or injects !terraform_state_bucket into an .env file."""
    if not env_file_path.exists():
        return

    content = env_file_path.read_text(encoding="utf-8")
    
    # Pattern to match !terraform_state_bucket = "..."
    pattern = re.compile(r'^!terraform_state_bucket\s*=.*$', re.MULTILINE)
    replacement = f'!terraform_state_bucket = "{bucket_name}"'

    if pattern.search(content):
        new_content = pattern.sub(replacement, content)
    else:
        # Append under [*] or at top of file
        new_content = replacement + "\n" + content

    env_file_path.write_text(new_content, encoding="utf-8")


def run_phase_2(repo_root: Path, outputs: dict):
    """
    Executes Phase 2: Injects generated S3 state bucket into environment files
    and invokes env-sync to dynamically generate backend.tfbackend and tfvars across all modules.
    """
    log_phase(2, 11, "Synchronize Environment & Generate Backend Configurations (env-sync)")
    bucket_name = outputs.get("terraform_state_bucket", "")
    
    if not bucket_name:
        log_error("Terraform state bucket name is missing from Phase 1 outputs.")
        raise ValueError("terraform_state_bucket output is empty.")

    log_info(f"Setting remote state bucket '{bucket_name}' in environment files...")

    # Update .env files across scopes
    env_files = [
        repo_root / "environments" / "global" / ".env.pre-infra",
        repo_root / "environments" / "global" / ".env.shared",
        repo_root / "environments" / "dev" / ".env.dev",
        repo_root / "environments" / "prod" / ".env.prod",
    ]

    for env_path in env_files:
        if env_path.exists():
            _update_env_file_backend_bucket(env_path, bucket_name)
            log_info(f"Updated backend bucket in: {env_path.relative_to(repo_root)}")

    # Execute env-sync to generate all backend.tfbackend and .tfvars
    success, changes, errors = synchronize_all(
        repo_root=str(repo_root),
        dry_run=False,
        validate_only=False,
    )

    if not success or errors:
        for err in errors:
            log_error(err)
        raise RuntimeError(f"env-sync failed during Phase 2: {errors}")

    log_success(f"Generated backend configurations and synced variables across all Terraform modules ({len(changes)} operations applied).")
