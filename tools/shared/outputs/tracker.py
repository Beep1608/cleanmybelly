"""
Generic execution tracking and incremental output reporting module for cleanmybelly CLI tools.
Maintains outputs/<tool_name>/outputs.json, outputs/<tool_name>/status.json, and outputs/<tool_name>/status.log dynamically.
"""

import json
import time
from pathlib import Path
from typing import List, Tuple, Optional

class ExecutionTracker:
    """Tracks phase execution status and outputs incrementally for any tool."""
    def __init__(
        self,
        repo_root: Path,
        tool_name: str,
        phases_definition: Optional[List[Tuple[int, str, str]]] = None
    ):
        self.repo_root = repo_root
        self.tool_name = tool_name
        self.phases_definition = phases_definition or []

        # Centralized outputs directory: outputs/<tool_name>/
        self.output_dir = repo_root / "outputs" / tool_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.outputs_file = self.output_dir / "outputs.json"
        self.status_json_file = self.output_dir / "status.json"
        self.status_log_file = self.output_dir / "status.log"

        self.total_phases = len(self.phases_definition)
        self.status_data = {
            "tool_name": tool_name,
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
                for num, name, target in self.phases_definition
            ]
        }
        self._init_files()

    def _now_iso(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _init_files(self):
        """Initializes status tracking files and log."""
        self._write_status_json()
        log_entry = f"[{self._now_iso()}] [INIT] Execution started for tool '{self.tool_name}'. {self.total_phases} phases registered.\n"
        self.status_log_file.write_text(log_entry, encoding="utf-8")

    def _write_status_json(self):
        self.status_data["last_updated"] = self._now_iso()
        self.status_json_file.write_text(json.dumps(self.status_data, indent=2), encoding="utf-8")

    def _append_log(self, text: str):
        with open(self.status_log_file, "a", encoding="utf-8") as f:
            f.write(f"[{self._now_iso()}] {text}\n")

    def save_incremental_outputs(self, outputs: dict):
        """Saves current state of outputs to outputs/<tool_name>/outputs.json incrementally."""
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
                self._append_log(f"[START] Phase {phase_num}/{self.total_phases}: {p['name']} (target: {p['target_dir']})")
                break
        self._write_status_json()

    def complete_phase(self, phase_num: int, outputs: dict):
        """Marks a phase as SUCCESS, updates outputs and status logs."""
        for p in self.status_data["phases"]:
            if p["phase_number"] == phase_num:
                p["status"] = "SUCCESS"
                p["end_time"] = self._now_iso()
                self._append_log(f"[SUCCESS] Phase {phase_num}/{self.total_phases}: {p['name']}")
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
                self._append_log(f"[FAILED] Phase {phase_num}/{self.total_phases}: {p['name']} - Error: {error_msg}")
                break
        self._write_status_json()

    def complete_all(self):
        """Marks overall status as SUCCESS upon completing all phases."""
        self.status_data["overall_status"] = "SUCCESS"
        self._append_log(f"[COMPLETE] All {self.total_phases} phases executed successfully.")
        self._write_status_json()
