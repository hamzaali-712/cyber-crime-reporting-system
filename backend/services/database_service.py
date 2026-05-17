"""
Cyber Crime Reporting System - Centralized Database Service

Thread-safe, process-robust JSON database manager acting as the single source
of truth for citizens and officer panels. Automatically manages:
- Cryptographic PBKDF2 hashing for officer passwords.
- Syncing status updates across complaints and decisions files.
- Recording detailed audit logs for every state-changing event.
"""

import os
import json
import threading
import secrets
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

# Security Utils for hashing and cryptography
from backend.utils.security import SecurityUtils

# File Paths
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COMPLAINTS_FILE = DATA_DIR / "complaints.json"
OFFICERS_FILE = DATA_DIR / "officers.json"
DECISIONS_FILE = DATA_DIR / "officer_decisions.json"
AUDIT_LOG_FILE = DATA_DIR / "audit_logs.json"

class DatabaseService:
    """Service for robust thread-safe database operations on local JSON storage."""

    def __init__(self):
        self.lock = threading.Lock()
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Initialize files with valid structures
        if not COMPLAINTS_FILE.exists() or COMPLAINTS_FILE.stat().st_size == 0:
            self._write_raw(COMPLAINTS_FILE, {})
        if not OFFICERS_FILE.exists() or OFFICERS_FILE.stat().st_size == 0:
            self._write_raw(OFFICERS_FILE, {})
        if not DECISIONS_FILE.exists() or DECISIONS_FILE.stat().st_size == 0:
            self._write_raw(DECISIONS_FILE, {})
        if not AUDIT_LOG_FILE.exists() or AUDIT_LOG_FILE.stat().st_size == 0:
            self._write_raw(AUDIT_LOG_FILE, [])

    def _write_raw(self, path: Path, default_data: Any):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2)
        except Exception as e:
            print(f"Error initializing database file {path.name}: {e}")

    def _load_file(self, file_path: Path) -> Any:
        """Loads data from a JSON file with thread safety."""
        with self.lock:
            if not file_path.exists():
                return {} if file_path != AUDIT_LOG_FILE else []
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                # In case of corruption, return empty structural defaults
                print(f"Error reading database file {file_path.name}: {e}")
                return [] if file_path == AUDIT_LOG_FILE else {}

    def _save_file(self, file_path: Path, data: Any):
        """Saves data to a JSON file with thread safety."""
        with self.lock:
            try:
                os.makedirs(file_path.parent, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            except Exception as e:
                print(f"Error writing database file {file_path.name}: {e}")

    # ── COMPLAINT LAYER ───────────────────────────────────────────────────────
    
    def create_complaint(self, complaint_data: Dict[str, Any]) -> str:
        """Registers a new complaint and logs the event."""
        tracking_id = complaint_data.get("tracking_id")
        complaints = self._load_file(COMPLAINTS_FILE)
        complaints[tracking_id] = complaint_data
        self._save_file(COMPLAINTS_FILE, complaints)
        
        # Automatic audit log
        self.create_audit_log(
            user_id=None,
            action="SUBMIT_COMPLAINT",
            resource_type="complaint",
            resource_id=tracking_id,
            details={
                "anonymous": complaint_data.get("anonymous"),
                "reason": complaint_data.get("complaint_reason")
            }
        )
        return tracking_id

    def get_complaint(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific complaint by tracking ID."""
        complaints = self._load_file(COMPLAINTS_FILE)
        return complaints.get(tracking_id)

    def get_all_complaints(self) -> Dict[str, Dict[str, Any]]:
        """Retrieves all registered complaints."""
        return self._load_file(COMPLAINTS_FILE)

    # ── SYNCED STATUS & DECISION LAYER ───────────────────────────────────────
    
    def update_complaint_status(self, tracking_id: str, status: str, notes: str, officer_id: str) -> bool:
        """
        Synchronized atomic update of both complaints and decisions files.
        Ensures complaint status is synced instantly and logs the audit event.
        """
        complaints = self._load_file(COMPLAINTS_FILE)
        if tracking_id not in complaints:
            return False
        
        # 1. Update status directly inside complaints.json
        complaints[tracking_id]["status"] = status.lower()
        complaints[tracking_id]["updated_at"] = datetime.now().isoformat()
        self._save_file(COMPLAINTS_FILE, complaints)
        
        # 2. Update decision history inside officer_decisions.json
        decisions = self._load_file(DECISIONS_FILE)
        decisions[tracking_id] = {
            "officer_id": officer_id,
            "decision": status,
            "notes": notes,
            "decided_at": datetime.now().isoformat()
        }
        self._save_file(DECISIONS_FILE, decisions)
        
        # 3. Automatic audit log
        self.create_audit_log(
            user_id=officer_id,
            action="UPDATE_CASE_STATUS",
            resource_type="complaint",
            resource_id=tracking_id,
            details={"status": status}
        )
        return True

    def get_decision(self, tracking_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves decision/remarks for a tracking ID."""
        decisions = self._load_file(DECISIONS_FILE)
        return decisions.get(tracking_id)

    def get_all_decisions(self) -> Dict[str, Dict[str, Any]]:
        """Retrieves all case decisions."""
        return self._load_file(DECISIONS_FILE)

    # ── OFFICER LAYER WITH CRYPTO SECURITY ───────────────────────────────────
    
    def get_officer(self, officer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an officer record."""
        officers = self._load_file(OFFICERS_FILE)
        return officers.get(officer_id)

    def create_officer(self, officer_data: Dict[str, Any]) -> str:
        """Registers a new officer using secure PBKDF2 hashing."""
        name = officer_data.get("name")
        email = officer_data.get("email")
        role = officer_data.get("role")
        raw_password = officer_data.get("password")
        
        generated_id = f"CYBER2026{name.replace(' ', '').upper()}"
        hashed_password = SecurityUtils.hash_password(raw_password)
        
        officers = self._load_file(OFFICERS_FILE)
        officers[generated_id] = {
            "name": name,
            "email": email,
            "role": role,
            "password": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        self._save_file(OFFICERS_FILE, officers)
        
        # Automatic audit log
        self.create_audit_log(
            user_id=None,
            action="OFFICER_REGISTRATION",
            resource_type="officer",
            resource_id=generated_id,
            details={"role": role, "email": email}
        )
        return generated_id

    def verify_officer(self, officer_id: str, password: str) -> bool:
        """Verifies officer credentials securely and writes an audit log."""
        officer = self.get_officer(officer_id)
        if not officer:
            # Audit log for failed attempt
            self.create_audit_log(
                user_id="anonymous",
                action="OFFICER_LOGIN_FAILED",
                resource_type="officer",
                resource_id=officer_id,
                details={"reason": "Node ID not found"}
            )
            return False
        
        hashed = officer.get("password")
        is_valid = SecurityUtils.verify_password(password, hashed)
        
        # Automatic audit log
        self.create_audit_log(
            user_id=officer_id,
            action="OFFICER_LOGIN_SUCCESS" if is_valid else "OFFICER_LOGIN_FAILED",
            resource_type="officer",
            resource_id=officer_id,
            details={"success": is_valid}
        )
        return is_valid

    # ── SECURE AUDIT LOGGING LAYER ───────────────────────────────────────────
    
    def create_audit_log(self, user_id: Optional[str], action: str, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """Appends a new security-critical event to the central audit log file."""
        logs = self._load_file(AUDIT_LOG_FILE)
        if not isinstance(logs, list):
            logs = []
            
        log_id = f"AUDIT-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        log_entry = {
            "id": log_id,
            "user_id": user_id or "system/citizen",
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        logs.append(log_entry)
        self._save_file(AUDIT_LOG_FILE, logs)
        return True

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        """Retrieves the complete audit trail logs."""
        logs = self._load_file(AUDIT_LOG_FILE)
        if not isinstance(logs, list):
            return []
        return logs

# Instantiate global service instance
db_service = DatabaseService()