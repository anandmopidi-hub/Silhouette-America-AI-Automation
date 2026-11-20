"""Serial Manager Module for Silhouette America AI Automation.

Implements automated, sequential machine serial-number generation, regex validation,
atomic JSON inventory management, duplicate prevention, and state tracking.
Adheres to the production QA machine serial specification:
    (?i)^[RVKT]\\d{3}P\\d{6}$
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import AutomationLogger

logger = AutomationLogger.get_logger(__name__)

# Production QA machine serial regex:
# Must start with R, V, K, or T, followed by 3 digits, the letter P, and 6 digits.
# Exactly 11 characters, case-insensitive.
SERIAL_REGEX = re.compile(r"^[RVKT]\d{3}P\d{6}$", re.IGNORECASE)

DEFAULT_CONFIG_PATH = Path("test_data") / "machines" / "machine_registration.json"
DEFAULT_HISTORY_PATH = Path("test_data") / "machines" / "serial_attempt_history.json"


class SerialManager:
    """Manages machine serial numbers, range validation, atomic JSON updates,

    sequential allocation, and duplicate prevention.
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        history_path: Optional[Path] = None,
    ) -> None:
        self.config_path = Path(config_path or DEFAULT_CONFIG_PATH)
        self.history_path = Path(history_path or DEFAULT_HISTORY_PATH)
        self._cached_config: Optional[Dict[str, Any]] = None

    # =========================================================================
    # 1. Regex Validation
    # =========================================================================

    @staticmethod
    def validate_serial_format(serial: Optional[str]) -> bool:
        """Validate serial format against the required regex: (?i)^[RVKT]\\d{3}P\\d{6}$."""
        if not serial or not isinstance(serial, str):
            return False
        return bool(SERIAL_REGEX.match(serial.strip()))

    # =========================================================================
    # 2. Configurable Range & Authorization Settings
    # =========================================================================

    def get_range_config(self) -> Dict[str, Any]:
        """Load and resolve configurable serial range settings from JSON or environment."""
        data = self._load_json(self.config_path)
        range_cfg = data.get("serial_range_config", {})

        # Environment variable overrides take precedence
        prefix = (
            os.getenv("MACHINE_SERIAL_PREFIX")
            or range_cfg.get("prefix")
            or "R250P"
        ).strip().upper()

        start_num = int(
            os.getenv("MACHINE_SERIAL_START_NUM")
            or range_cfg.get("start_number")
            or 567850
        )

        candidate_limit = int(
            os.getenv("MACHINE_SERIAL_LIMIT")
            or range_cfg.get("candidate_limit")
            or 500
        )

        end_num = int(
            os.getenv("MACHINE_SERIAL_END_NUM")
            or range_cfg.get("end_number")
            or (start_num + candidate_limit - 1)
        )

        admin_auth_env = os.getenv("ADMIN_SERIAL_RANGE_AUTHORIZED")
        if admin_auth_env is not None:
            admin_authorized = admin_auth_env.strip().lower() in ("1", "true", "yes")
        else:
            admin_authorized = bool(range_cfg.get("admin_range_authorized", False))

        return {
            "prefix": prefix,
            "start_number": start_num,
            "end_number": end_num,
            "candidate_limit": candidate_limit,
            "admin_range_authorized": admin_authorized,
        }

    def is_admin_range_authorized(self) -> bool:
        """Check whether the configured production serial range has been Admin-authorized."""
        return self.get_range_config().get("admin_range_authorized", False)

    # =========================================================================
    # 3. Dynamic Sequential Candidate Generation (Up to 500)
    # =========================================================================

    def generate_candidates(self, limit: Optional[int] = None) -> List[str]:
        """Dynamically generate sequential serial candidates based on range configuration.

        Does not require manual maintenance of 500 serial numbers in the JSON file.
        Each candidate is verified against (?i)^[RVKT]\\d{3}P\\d{6}$.
        """
        cfg = self.get_range_config()
        prefix = cfg["prefix"]
        start_num = cfg["start_number"]
        end_num = cfg["end_number"]
        max_limit = limit if limit is not None else cfg["candidate_limit"]

        # Ensure prefix ends with 'P' and conforms to prefix requirement
        if not prefix.endswith("P"):
            prefix = f"{prefix}P"

        candidates: List[str] = []
        current_num = start_num
        while current_num <= end_num and len(candidates) < max_limit:
            candidate = f"{prefix}{current_num:06d}"
            if self.validate_serial_format(candidate):
                candidates.append(candidate)
            else:
                logger.warning(f"Generated candidate '{candidate}' failed regex format validation. Skipping.")
            current_num += 1

        return candidates

    # =========================================================================
    # 4. Atomic JSON Persistence & Inventory Management
    # =========================================================================

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Safely load JSON file contents or return empty dictionary if not found."""
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read JSON at '{path}': {e}")
        return {}

    def _save_json_atomic(self, path: Path, data: Dict[str, Any]) -> None:
        """Save JSON data atomically via temporary file replacement.

        Protects against file corruption and race conditions during concurrent runs.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.parent / f"{path.name}.tmp.{os.getpid()}.{int(time.time() * 1000)}"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, path)
        except Exception as e:
            logger.error(f"Atomic write to '{path}' failed: {e}")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            raise

    def get_registration_history(self) -> List[Dict[str, Any]]:
        """Retrieve full registration history records from machine_registration.json.

        Maintains: serial, status, used_date, test_case_id.
        """
        data = self._load_json(self.config_path)
        history = data.get("registration_history", [])
        if not isinstance(history, list):
            history = []
        return history

    def get_serial_record(self, serial: str) -> Optional[Dict[str, Any]]:
        """Retrieve record for a specific serial from history."""
        target = serial.strip().upper()
        for item in self.get_registration_history():
            if item.get("serial", "").strip().upper() == target:
                return item
        return None

    def update_serial_status(
        self,
        serial: str,
        status: str,
        test_case_id: str = "E2E-MACHINE-001",
        used_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Atomically record or update a candidate's status, used date, and test case ID.

        Statuses: 'Available', 'Used', 'already_registered', 'invalid', 'blocked'.
        """
        norm_serial = serial.strip().upper()
        timestamp = used_date or time.strftime("%Y-%m-%dT%H:%M:%S")

        data = self._load_json(self.config_path)
        history = data.get("registration_history", [])
        if not isinstance(history, list):
            history = []

        # Find existing or append new entry
        found = False
        target_record: Dict[str, Any] = {}
        for record in history:
            if record.get("serial", "").strip().upper() == norm_serial:
                record["status"] = status
                record["used_date"] = timestamp
                record["test_case_id"] = test_case_id
                if notes:
                    record["notes"] = notes
                target_record = record
                found = True
                break

        if not found:
            target_record = {
                "serial": norm_serial,
                "status": status,
                "used_date": timestamp,
                "test_case_id": test_case_id,
            }
            if notes:
                target_record["notes"] = notes
            history.append(target_record)

        data["registration_history"] = history

        # Also keep starting_serial pointer synchronized with latest candidate
        if status in ("Used", "already_registered"):
            data["last_evaluated_serial"] = norm_serial

        self._save_json_atomic(self.config_path, data)

        # Synchronize with legacy serial_attempt_history.json for backward compatibility
        self._sync_legacy_history(norm_serial, status, notes or f"Updated by {test_case_id}")

        logger.info(
            f"SerialManager: Updated '{norm_serial}' -> status='{status}', "
            f"test_case_id='{test_case_id}', used_date='{timestamp}'"
        )
        return target_record

    def _sync_legacy_history(self, serial: str, status: str, message: str) -> None:
        """Mirror update to serial_attempt_history.json."""
        try:
            hist_data = self._load_json(self.history_path)
            hist_status = "ALREADY_REGISTERED" if status == "already_registered" else (
                "USED" if status == "Used" else status.upper()
            )
            hist_data[serial] = {
                "status": hist_status,
                "message": message[:200],
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            self._save_json_atomic(self.history_path, hist_data)
        except Exception as e:
            logger.debug(f"Legacy history sync notice for '{serial}': {e}")

    # =========================================================================
    # 5. Sequential Allocation & Duplicate Prevention
    # =========================================================================

    def get_next_eligible_serial(self, max_candidates: Optional[int] = None) -> Optional[str]:
        """Find the next eligible sequential candidate from the configured range.

        Guarantees:
        - Validates format with (?i)^[RVKT]\\d{3}P\\d{6}$.
        - Skips serials with status 'Used', 'already_registered', or 'invalid'.
        - Prevents re-use of previously registered serials.
        - Returns None if range is exhausted.
        """
        candidates = self.generate_candidates(limit=max_candidates)
        history = {r.get("serial", "").strip().upper(): r for r in self.get_registration_history()}

        for candidate in candidates:
            c_norm = candidate.strip().upper()
            record = history.get(c_norm)

            if record:
                rec_status = record.get("status", "").lower()
                # If already used, registered, or marked invalid, skip
                if rec_status in ("used", "already_registered", "invalid", "blocked"):
                    continue

            # Double check regex format
            if not self.validate_serial_format(c_norm):
                self.update_serial_status(c_norm, "invalid", notes="Failed regex format check")
                continue

            return c_norm

        logger.warning(
            f"SerialManager: No eligible unregistered serial candidates available across {len(candidates)} "
            f"generated candidates in range."
        )
        return None

    def get_candidate_evaluation_list(self, max_retries: int = 5) -> List[str]:
        """Retrieve the next batch of up to `max_retries` un-used candidates for sequential evaluation."""
        candidates = self.generate_candidates()
        history = {r.get("serial", "").strip().upper(): r for r in self.get_registration_history()}

        batch: List[str] = []
        for candidate in candidates:
            c_norm = candidate.strip().upper()
            record = history.get(c_norm)
            if record and record.get("status", "").lower() in ("used", "already_registered", "invalid", "blocked"):
                continue
            if self.validate_serial_format(c_norm):
                batch.append(c_norm)
                if len(batch) >= max_retries:
                    break
        return batch
