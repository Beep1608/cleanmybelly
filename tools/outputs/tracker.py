"""
Execution tracking and incremental output reporting module for the cleanmybelly Bootstrap CLI tool.
Maintains tools/bootstrap_outputs.json, tools/bootstrap_status.json, and tools/bootstrap_status.log dynamically.
"""

import json
import time
from pathlib import Path

PHASE_DEFINITIONS = [
    (1, "Bootstrap S3 Remote State Bucket", "aws/pre-infra/bootstrap"),
    (2, "Global Provider Find & Replace", "workspace"),
    (3, "Deploy IAM Local Deployer User", "aws/pre-infra/iam-deployer"),
    (4, "Configure AWS CLI Profile (terraform-user)", "local-aws-profile"),
    (5, "Provision GitHub Repository", "aws/pre-infra/github/repository"),
    (6, "Connect Local Clone to GitHub Repository", "git-remote"),
    (7, "Deploy OIDC Federation", "aws/pre-infra/github/oidc"),
    (8, "Secrets & Workflow Publishing", "aws/pre-infra/github/secrets-workflow"),
    (9, "Route 53 DNS Hosted Zone", "aws/infra/shared/networking/dns-zone"),
    (10, "Registrar Setup & Name Server Verification", "manual-registrar"),
    (11, "ACM SSL Certificates", "aws/infra/shared/networking/certificates"),
]

class ExecutionTracker:
    """Tracks phase execution status and outputs incrementally."""
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.tools_dir = repo_root / "tools"
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        self.outputs_file = self.tools_dir / "bootstrap_outputs.json"
        self.status_json_file = self.tools_dir / "bootstrap_status.json"
        self.status_log_file = self.tools_dir / "bootstrap_status.log"

        self.status_data = {
            "start_time": self._now_iso(),
            "last_updated": self._now_iso(),
            "overall_status": "IN_PROGRESS",
            "current_phase": 0,
            "phases": [
                {
                    "phase_number": num,
                    "name": name,
                    "target_dir": target,
                    "status": "PENDING",
                    "start_time": None,
                    "end_time": None,
                    "error_message": None
                }
                for num, name, target in PHASE_DEFINITIONS
            ]
        }
        self._init_files()

    def _now_iso(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _init_files(self):
        """Initializes status tracking files and log."""
        self._write_status_json()
        log_entry = f"[{self._now_iso()}] [INIT] Bootstrap execution started. 11 phases registered.\n"
        self.status_log_file.write_text(log_entry, encoding="utf-8")

    def _write_status_json(self):
        self.status_data["last_updated"] = self._now_iso()
        self.status_json_file.write_text(json.dumps(self.status_data, indent=2), encoding="utf-8")

    def _append_log(self, text: str):
        with open(self.status_log_file, "a", encoding="utf-8") as f:
            f.write(f"[{self._now_iso()}] {text}\n")

    def save_incremental_outputs(self, outputs: dict):
        """Saves current state of outputs to tools/bootstrap_outputs.json incrementally."""
        save_data = outputs.copy()
        save_data["timestamp"] = self._now_iso()
        if "iam_deployer_secret_access_key" in save_data and save_data["iam_deployer_secret_access_key"]:
            save_data["iam_deployer_secret_access_key"] = "[CONFIGURED IN AWS PROFILE 'terraform-user']"

        self.outputs_file.write_text(json.dumps(save_data, indent=2), encoding="utf-8")

    def start_phase(self, phase_num: int):
        """Marks a phase as IN_PROGRESS and updates logs."""
        self.status_data["current_phase"] = phase_num
        for p in self.status_data["phases"]:
            if p["phase_number"] == phase_num:
                p["status"] = "IN_PROGRESS"
                p["start_time"] = self._now_iso()
                self._append_log(f"[START] Phase {phase_num}/11: {p['name']} (target: {p['target_dir']})")
                break
        self._write_status_json()

    def complete_phase(self, phase_num: int, outputs: dict):
        """Marks a phase as SUCCESS, updates outputs and status logs."""
        for p in self.status_data["phases"]:
            if p["phase_number"] == phase_num:
                p["status"] = "SUCCESS"
                p["end_time"] = self._now_iso()
                self._append_log(f"[SUCCESS] Phase {phase_num}/11: {p['name']}")
                break
        self.save_incremental_outputs(outputs)
        self._write_status_json()

    def fail_phase(self, phase_num: int, error_msg: str):
        """Marks current phase and overall status as FAILED."""
        self.status_data["overall_status"] = "FAILED"
        for p in self.status_data["phases"]:
            if p["phase_number"] == phase_num:
                p["status"] = "FAILED"
                p["end_time"] = self._now_iso()
                p["error_message"] = str(error_msg)
                self._append_log(f"[FAILED] Phase {phase_num}/11: {p['name']} - Error: {error_msg}")
                break
        self._write_status_json()

    def complete_all(self):
        """Marks overall status as SUCCESS upon completing all phases."""
        self.status_data["overall_status"] = "SUCCESS"
        self._append_log("[COMPLETE] All 11 bootstrap phases executed successfully.")
        self._write_status_json()
