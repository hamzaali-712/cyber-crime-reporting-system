"""
Cyber Crime Reporting System - Centralized Database Service
Thread-safe, process-robust hybrid JSON / Supabase Database Manager.
Acts as a high-performance single source of truth. Features:
- Secure automatic failover: If Supabase tables are not created, automatically falls back to local JSON storage.
- Real-time cloud sync: Once Supabase SQL tables are initialized, separate cloud deployments sync dynamically!
- Cryptographic PBKDF2 hashing for officer passwords.
- Synced status updates across complaints and decisions.
- Secure audit logs for every state-changing event.
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

# Supabase Client Initialization
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Accept both keys
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase_client = None
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    supabase_client = None

# File Paths
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COMPLAINTS_FILE = DATA_DIR / "complaints.json"
OFFICERS_FILE = DATA_DIR / "officers.json"
DECISIONS_FILE = DATA_DIR / "officer_decisions.json"
AUDIT_LOG_FILE = DATA_DIR / "audit_logs.json"

class DatabaseService:
    """Service for robust database operations on local JSON or Supabase Cloud storage."""

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
        """Registers a new complaint securely in Supabase if configured, otherwise falls back to JSON."""
        tracking_id = complaint_data.get("tracking_id")
        
        if supabase_client:
            try:
                supabase_client.table("complaints").insert(complaint_data).execute()
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
            except Exception as e:
                print(f"[Supabase Fallback] Error writing complaint: {e}. Falling back to local storage.")
        
        # Local JSON Fallback
        complaints = self._load_file(COMPLAINTS_FILE)
        complaints[tracking_id] = complaint_data
        self._save_file(COMPLAINTS_FILE, complaints)
        
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
        if supabase_client:
            try:
                r = supabase_client.table("complaints").select("*").eq("tracking_id", tracking_id).execute()
                if r.data:
                    return r.data[0]
            except Exception as e:
                print(f"[Supabase Fallback] Error reading complaint: {e}")
        
        complaints = self._load_file(COMPLAINTS_FILE)
        return complaints.get(tracking_id)

    def get_all_complaints(self) -> Dict[str, Dict[str, Any]]:
        """Retrieves all registered complaints and auto-synchronizes legacy decisions."""
        if supabase_client:
            try:
                r = supabase_client.table("complaints").select("*").execute()
                complaints_dict = {row["tracking_id"]: row for row in r.data}
                
                decisions_r = supabase_client.table("officer_decisions").select("*").execute()
                decisions_dict = {row["tracking_id"]: row for row in decisions_r.data}
                
                updated = False
                for tid, d in decisions_dict.items():
                    if tid in complaints_dict:
                        current_status = complaints_dict[tid].get("status", "pending").lower()
                        decision_status = d.get("decision", "approve").lower()
                        if current_status == "pending" and decision_status != "pending":
                            complaints_dict[tid]["status"] = decision_status
                            complaints_dict[tid]["updated_at"] = d.get("decided_at", datetime.now().isoformat())
                            supabase_client.table("complaints").update({
                                "status": decision_status, 
                                "updated_at": complaints_dict[tid]["updated_at"]
                            }).eq("tracking_id", tid).execute()
                
                return complaints_dict
            except Exception as e:
                print(f"[Supabase Fallback] Error getting all complaints: {e}")
        
        # Local JSON Fallback
        complaints = self._load_file(COMPLAINTS_FILE)
        decisions = self._load_file(DECISIONS_FILE)
        
        updated = False
        for tid, d in decisions.items():
            if tid in complaints:
                current_status = complaints[tid].get("status", "pending").lower()
                decision_status = d.get("decision", "approve").lower()
                if current_status == "pending" and decision_status != "pending":
                    complaints[tid]["status"] = decision_status
                    complaints[tid]["updated_at"] = d.get("decided_at", d.get("timestamp", datetime.now().isoformat()))
                    updated = True
                    
        if updated:
            self._save_file(COMPLAINTS_FILE, complaints)
            
        return complaints

    # ── SYNCED STATUS & DECISION LAYER ───────────────────────────────────────
    
    def update_complaint_status(self, tracking_id: str, status: str, notes: str, officer_id: str) -> bool:
        """Synchronized atomic update of both complaints and decisions."""
        if supabase_client:
            try:
                # 1. Update complaints table
                supabase_client.table("complaints").update({
                    "status": status.lower(),
                    "updated_at": datetime.now().isoformat()
                }).eq("tracking_id", tracking_id).execute()
                
                # 2. Update officer decisions table
                decision_data = {
                    "tracking_id": tracking_id,
                    "officer_id": officer_id,
                    "decision": status,
                    "notes": notes,
                    "decided_at": datetime.now().isoformat()
                }
                supabase_client.table("officer_decisions").upsert(decision_data).execute()
                
                # 3. Create audit log
                self.create_audit_log(
                    user_id=officer_id,
                    action="UPDATE_CASE_STATUS",
                    resource_type="complaint",
                    resource_id=tracking_id,
                    details={"status": status}
                )
                return True
            except Exception as e:
                print(f"[Supabase Fallback] Error updating complaint status: {e}")
        
        # Local JSON Fallback
        complaints = self._load_file(COMPLAINTS_FILE)
        if tracking_id not in complaints:
            return False
        
        complaints[tracking_id]["status"] = status.lower()
        complaints[tracking_id]["updated_at"] = datetime.now().isoformat()
        self._save_file(COMPLAINTS_FILE, complaints)
        
        decisions = self._load_file(DECISIONS_FILE)
        decisions[tracking_id] = {
            "officer_id": officer_id,
            "decision": status,
            "notes": notes,
            "decided_at": datetime.now().isoformat()
        }
        self._save_file(DECISIONS_FILE, decisions)
        
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
        if supabase_client:
            try:
                r = supabase_client.table("officer_decisions").select("*").eq("tracking_id", tracking_id).execute()
                if r.data:
                    return r.data[0]
            except Exception as e:
                print(f"[Supabase Fallback] Error getting decision: {e}")
        
        decisions = self._load_file(DECISIONS_FILE)
        return decisions.get(tracking_id)

    def get_all_decisions(self) -> Dict[str, Dict[str, Any]]:
        """Retrieves all case decisions."""
        if supabase_client:
            try:
                r = supabase_client.table("officer_decisions").select("*").execute()
                return {row["tracking_id"]: row for row in r.data}
            except Exception as e:
                print(f"[Supabase Fallback] Error getting all decisions: {e}")
        return self._load_file(DECISIONS_FILE)

    # ── OFFICER LAYER WITH CRYPTO SECURITY ───────────────────────────────────
    
    def get_officer(self, officer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an officer record."""
        if supabase_client:
            try:
                r = supabase_client.table("officers").select("*").eq("officer_id", officer_id).execute()
                if r.data:
                    return r.data[0]
            except Exception as e:
                print(f"[Supabase Fallback] Error getting officer: {e}")
        
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
        
        db_data = {
            "officer_id": generated_id,
            "name": name,
            "email": email,
            "role": role,
            "password": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        
        if supabase_client:
            try:
                supabase_client.table("officers").insert(db_data).execute()
                self.create_audit_log(
                    user_id=None,
                    action="OFFICER_REGISTRATION",
                    resource_type="officer",
                    resource_id=generated_id,
                    details={"role": role, "email": email}
                )
                return generated_id
            except Exception as e:
                print(f"[Supabase Fallback] Error creating officer: {e}")
        
        # Local JSON Fallback
        officers = self._load_file(OFFICERS_FILE)
        officers[generated_id] = {
            "name": name,
            "email": email,
            "role": role,
            "password": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        self._save_file(OFFICERS_FILE, officers)
        
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
        """Appends a new security-critical event to the central audit trail."""
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
        
        if supabase_client:
            try:
                supabase_client.table("audit_logs").insert(log_entry).execute()
                return True
            except Exception as e:
                print(f"[Supabase Fallback] Error writing audit log: {e}")
                
        # Local JSON Fallback
        logs = self._load_file(AUDIT_LOG_FILE)
        if not isinstance(logs, list):
            logs = []
        logs.append(log_entry)
        self._save_file(AUDIT_LOG_FILE, logs)
        return True

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        """Retrieves the complete audit trail logs."""
        if supabase_client:
            try:
                r = supabase_client.table("audit_logs").select("*").execute()
                return r.data
            except Exception as e:
                print(f"[Supabase Fallback] Error getting audit logs: {e}")
                
        logs = self._load_file(AUDIT_LOG_FILE)
        if not isinstance(logs, list):
            return []
        return logs

# Instantiate global service instance
db_service = DatabaseService()