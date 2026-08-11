"""
Phase 2: Global Find & Replace State Bucket Placeholder in providers.tf.
"""

from pathlib import Path
from tools.shared.ui import log_phase, log_info, log_success

def run_phase_2(repo_root: Path, outputs: dict):
    """Executes Phase 2: Performs workspace-wide Find & Replace for S3 state bucket."""
    log_phase(2, 11, "Global Find & Replace State Bucket Placeholder in providers.tf")
    bucket_name = outputs["terraform_state_bucket"]
    
    placeholders = [
        "<TERRAFORM_STATE_BUCKET_NAME>",
        "<YOUR_TFSTATE_BUCKET_NAME>",
        "<YOUR_GENERATED_BUCKET_NAME>"
    ]
    
    updated_count = 0
    aws_dir = repo_root / "aws"
    
    for tf_file in aws_dir.rglob("*.tf"):
        content = tf_file.read_text(encoding="utf-8")
        modified = False
        for ph in placeholders:
            if ph in content:
                content = content.replace(ph, bucket_name)
                modified = True
        if modified:
            tf_file.write_text(content, encoding="utf-8")
            updated_count += 1
            log_info(f"Updated: {tf_file.relative_to(repo_root)}")

    log_success(f"Updated state bucket in {updated_count} Terraform configuration files.")
