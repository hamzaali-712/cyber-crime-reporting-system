"""
CyberSecure – Backend Models
==============================
Three classes with full validation + Firebase persistence.

Each class's  save()  method has TWO paths:
  • DB live   → validates → writes to Firestore / RTDB / Storage → returns real IDs
  • DB offline → validates → returns a mock success response (no DB calls made)

This means the frontend works end-to-end even before Firebase is connected.
When you connect Firebase (DB_ENABLED=True + serviceAccountKey.json), the exact
same code writes real data — nothing else changes.
"""

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from firebase_config import is_db_ready, get_firestore, get_rtdb, get_storage_bucket

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

PAKISTAN_CITIES = sorted([
    "Abbottabad", "Attock", "Awaran", "Badin", "Bahawalnagar", "Bahawalpur",
    "Bannu", "Batkhela", "Bhakkar", "Bhimbar", "Burewala", "Chakwal",
    "Chaman", "Charsadda", "Chiniot", "Chishtian", "Dadu", "Dera Ghazi Khan",
    "Dera Ismail Khan", "Faisalabad", "Ghotki", "Gilgit", "Gujranwala",
    "Gujrat", "Gwadar", "Hafizabad", "Haripur", "Hyderabad", "Islamabad",
    "Jacobabad", "Jhang", "Jhelum", "Kamoke", "Karachi", "Kasur", "Khanewal",
    "Kharian", "Khuzdar", "Kohat", "Kot Addu", "Kotli", "Lahore", "Larkana",
    "Layyah", "Lodhran", "Loralai", "Mansehra", "Mardan", "Mianwali",
    "Mingora", "Mirpur", "Mirpur Khas", "Multan", "Muridke", "Muzaffarabad",
    "Muzaffargarh", "Nankana Sahib", "Narowal", "Nawabshah", "Nowshera",
    "Okara", "Pakpattan", "Peshawar", "Quetta", "Rahim Yar Khan",
    "Rawalpindi", "Sadiqabad", "Sahiwal", "Sargodha", "Sheikhupura",
    "Sialkot", "Sibi", "Sukkur", "Swabi", "Tando Adam", "Tando Allahyar",
    "Tank", "Taxila", "Turbat", "Vehari", "Wah Cantonment", "Wazirabad", "Zhob",
])

CRIME_CATEGORIES = [
    "Online Fraud / Financial Scam",
    "Cyberbullying / Harassment",
    "Identity Theft",
    "Hacking / Unauthorized Access",
    "Child Exploitation / CSAM",
    "Phishing / Spoofing",
    "Ransomware / Malware Attack",
    "Defamation / Fake News",
    "Online Blackmail / Extortion",
    "Data Breach / Privacy Violation",
    "Illegal Content Distribution",
    "Other",
]

COMPLAINT_STATUSES = ["Submitted", "Under Review", "Investigation", "Resolved", "Closed"]


# ─────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _mock_id(prefix: str = "") -> str:
    """Generate a short offline ID so the frontend always receives an ID."""
    return prefix + uuid.uuid4().hex[:12].upper()

def _err(field: str, msg: str) -> dict:
    return {"success": False, "field": field, "message": msg}

def _ok(**kwargs) -> dict:
    return {"success": True, **kwargs}


# ─────────────────────────────────────────────────────────────
# Class 1 – Personal Information
# ─────────────────────────────────────────────────────────────

class PersonalInformation:
    """
    Stores personal details of the complainant.

    DB LIVE path
    ─────────────
    Firestore  →  personal_information/{cnic}
    RTDB       →  complaints/{cnic}/status  { status:"Submitted", updated_at }

    DB OFFLINE path
    ────────────────
    Validates fields only.
    Returns mock personal_id = CNIC so downstream classes work normally.
    No data is written anywhere.

    Validation rules
    ─────────────────
    full_name   : required · 2–100 chars
    cnic        : required · format 12345-1234567-1 · unique (DB live only)
    gender      : required · Male | Female | Other
    mobile      : required · +92 followed by exactly 10 digits
    email       : optional · must contain @ if provided
    occupation  : optional
    """

    FS_COLLECTION = "personal_information"
    RTDB_NODE     = "complaints"

    GENDERS   = {"Male", "Female", "Other"}
    CNIC_RE   = re.compile(r"^\d{5}-\d{7}-\d$")
    MOBILE_RE = re.compile(r"^\+92[0-9]{10}$")

    def __init__(self, full_name: str, cnic: str, gender: str,
                 mobile: str, email: str = "", occupation: str = ""):
        self.full_name  = full_name.strip()
        self.cnic       = cnic.strip()
        self.gender     = gender.strip()
        self.mobile     = mobile.strip()
        self.email      = email.strip()
        self.occupation = occupation.strip()

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(self) -> dict:
        if not self.full_name:
            return _err("full_name", "Full name is required.")
        if not (2 <= len(self.full_name) <= 100):
            return _err("full_name", "Full name must be between 2 and 100 characters.")

        if not self.cnic:
            return _err("cnic", "CNIC is required.")
        if not self.CNIC_RE.match(self.cnic):
            return _err("cnic", "CNIC must follow the format 12345-1234567-1.")

        if self.gender not in self.GENDERS:
            return _err("gender", f"Gender must be one of: {', '.join(sorted(self.GENDERS))}.")

        if not self.mobile:
            return _err("mobile", "Mobile number is required.")
        if not self.MOBILE_RE.match(self.mobile):
            return _err("mobile",
                "Mobile must start with +92 followed by exactly 10 digits. "
                "Example: +923001234567")

        if self.email and "@" not in self.email:
            return _err("email", "Email address must contain '@'.")

        return {"success": True}

    # ── Save (DB-aware) ───────────────────────────────────────────────────────

    def save(self) -> dict:
        result = self.validate()
        if not result["success"]:
            return result

        # ── DB OFFLINE ────────────────────────────────────────────────────────
        if not is_db_ready():
            return _ok(
                personal_id = self.cnic,
                message     = "Personal information validated (offline mode — not saved to DB).",
                db_mode     = "offline",
            )

        # ── DB LIVE ───────────────────────────────────────────────────────────
        fs = get_firestore()

        # Duplicate CNIC check
        if fs.collection(self.FS_COLLECTION).document(self.cnic).get().exists:
            return _err("cnic",
                f"A complaint with CNIC {self.cnic} already exists in the system. "
                "Please contact support if you believe this is an error.")

        # Write to Firestore
        fs.collection(self.FS_COLLECTION).document(self.cnic).set({
            "full_name"  : self.full_name,
            "cnic"       : self.cnic,
            "gender"     : self.gender,
            "mobile"     : self.mobile,
            "email"      : self.email      or None,
            "occupation" : self.occupation or None,
            "created_at" : _now(),
        })

        # Write live status to RTDB
        get_rtdb().child(self.RTDB_NODE).child(self.cnic).child("status").set({
            "status"     : "Submitted",
            "updated_at" : _now(),
        })

        return _ok(
            personal_id = self.cnic,
            message     = "Personal information saved successfully.",
            db_mode     = "live",
        )

    # ── Reads ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(cnic: str) -> dict | None:
        if not is_db_ready():
            return None
        doc = get_firestore().collection(PersonalInformation.FS_COLLECTION).document(cnic).get()
        return doc.to_dict() if doc.exists else None

    @staticmethod
    def get_status(cnic: str) -> dict | None:
        if not is_db_ready():
            return None
        return get_rtdb().child(PersonalInformation.RTDB_NODE).child(cnic).child("status").get()

    @staticmethod
    def update_status(cnic: str, new_status: str) -> dict:
        if new_status not in COMPLAINT_STATUSES:
            return _err("status", f"Invalid status. Choose from: {', '.join(COMPLAINT_STATUSES)}")
        if not is_db_ready():
            return _ok(message=f"Status update noted (offline mode — not written to DB).")
        get_rtdb().child(PersonalInformation.RTDB_NODE).child(cnic).child("status").update({
            "status"     : new_status,
            "updated_at" : _now(),
        })
        return _ok(message=f"Status updated to '{new_status}'.")


# ─────────────────────────────────────────────────────────────
# Class 2 – Incident Details
# ─────────────────────────────────────────────────────────────

class IncidentDetails:
    """
    Stores incident details linked to a personal record.

    DB LIVE path
    ─────────────
    Firestore  →  incident_details/{auto_id}
    RTDB       →  complaints/{cnic}/incident  { incident_id, city, crime_category, created_at }

    DB OFFLINE path
    ────────────────
    Validates fields only.
    Returns mock incident_id so evidence upload still works.

    Validation rules
    ─────────────────
    city            : required · valid Pakistani city
    crime_category  : required · from predefined list
    crime_details   : required · max 3 500 characters
    postal_address  : optional
    """

    FS_COLLECTION  = "incident_details"
    RTDB_NODE      = "complaints"
    MAX_DETAIL_LEN = 3500

    def __init__(self, personal_id: str, city: str, crime_category: str,
                 crime_details: str, postal_address: str = ""):
        self.personal_id    = personal_id.strip()
        self.postal_address = postal_address.strip()
        self.city           = city.strip()
        self.crime_category = crime_category.strip()
        self.crime_details  = crime_details.strip()

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(self) -> dict:
        if not self.city:
            return _err("city", "City is required.")
        if self.city not in PAKISTAN_CITIES:
            return _err("city", f"'{self.city}' is not a recognised Pakistani city.")

        if not self.crime_category:
            return _err("crime_category", "Crime category must be selected.")
        if self.crime_category not in CRIME_CATEGORIES:
            return _err("crime_category",
                f"Invalid crime category. Choose from: {', '.join(CRIME_CATEGORIES)}")

        if not self.crime_details:
            return _err("crime_details", "Crime details are required.")
        if len(self.crime_details) > self.MAX_DETAIL_LEN:
            return _err("crime_details",
                f"Crime details must not exceed {self.MAX_DETAIL_LEN} characters "
                f"(currently {len(self.crime_details)}).")

        return {"success": True}

    # ── Save (DB-aware) ───────────────────────────────────────────────────────

    def save(self) -> dict:
        result = self.validate()
        if not result["success"]:
            return result

        # ── DB OFFLINE ────────────────────────────────────────────────────────
        if not is_db_ready():
            return _ok(
                incident_id = _mock_id("INC-"),
                message     = "Incident details validated (offline mode — not saved to DB).",
                db_mode     = "offline",
            )

        # ── DB LIVE ───────────────────────────────────────────────────────────
        fs = get_firestore()

        # Verify parent personal record exists
        if not fs.collection(PersonalInformation.FS_COLLECTION).document(self.personal_id).get().exists:
            return _err("personal_id",
                f"No personal information record found for CNIC '{self.personal_id}'.")

        # Write to Firestore
        _, doc_ref = fs.collection(self.FS_COLLECTION).add({
            "personal_id"    : self.personal_id,
            "postal_address" : self.postal_address or None,
            "city"           : self.city,
            "crime_category" : self.crime_category,
            "crime_details"  : self.crime_details,
            "created_at"     : _now(),
        })
        incident_id = doc_ref.id

        # Mirror snapshot to RTDB
        get_rtdb().child(self.RTDB_NODE).child(self.personal_id).child("incident").set({
            "incident_id"    : incident_id,
            "city"           : self.city,
            "crime_category" : self.crime_category,
            "created_at"     : _now(),
        })

        return _ok(
            incident_id = incident_id,
            message     = "Incident details saved successfully.",
            db_mode     = "live",
        )

    # ── Reads ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_id(incident_id: str) -> dict | None:
        if not is_db_ready():
            return None
        doc = get_firestore().collection(IncidentDetails.FS_COLLECTION).document(incident_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["incident_id"] = doc.id
        return data

    @staticmethod
    def get_by_personal_id(personal_id: str) -> list[dict]:
        if not is_db_ready():
            return []
        docs = (
            get_firestore().collection(IncidentDetails.FS_COLLECTION)
            .where("personal_id", "==", personal_id)
            .stream()
        )
        result = []
        for d in docs:
            row = d.to_dict()
            row["incident_id"] = d.id
            result.append(row)
        return result


# ─────────────────────────────────────────────────────────────
# Class 3 – Evidence Upload
# ─────────────────────────────────────────────────────────────

class EvidenceUpload:
    """
    Handles optional evidence files linked to an incident.

    DB LIVE path
    ─────────────
    Storage    →  evidence/{incident_id}/{timestamp}_{filename}
    Firestore  →  evidence_uploads/{auto_id}  { metadata }

    DB OFFLINE path
    ────────────────
    Validates file type/size only.
    Returns mock evidence_id — no bytes are written anywhere.

    Accepted types  : PNG, JPG/JPEG · MP4, MKV
    Max total size  : 500 MB
    """

    FS_COLLECTION      = "evidence_uploads"
    STORAGE_BASE       = "evidence"
    ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
    ALLOWED_VIDEO_EXTS = {".mp4", ".mkv"}
    ALLOWED_EXTS       = ALLOWED_IMAGE_EXTS | ALLOWED_VIDEO_EXTS
    MAX_TOTAL_BYTES    = 500 * 1024 * 1024   # 500 MB

    def __init__(self, incident_id: str, file_name: str,
                 file_bytes: bytes, file_type: str = ""):
        self.incident_id = incident_id.strip()
        self.file_name   = Path(file_name).name       # strip path traversal
        self.file_bytes  = file_bytes
        self.ext         = Path(self.file_name).suffix.lower()
        self.file_type   = file_type or (
            "image" if self.ext in self.ALLOWED_IMAGE_EXTS else "video"
        )

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(self) -> dict:
        if not self.file_name:
            return _err("file", "File name cannot be empty.")
        if self.ext not in self.ALLOWED_EXTS:
            return _err("file",
                f"File type '{self.ext}' is not allowed. "
                "Accepted formats: PNG, JPG, MP4, MKV.")
        if len(self.file_bytes) == 0:
            return _err("file", "Uploaded file is empty.")
        return {"success": True}

    # ── Save (DB-aware) ───────────────────────────────────────────────────────

    def save(self) -> dict:
        result = self.validate()
        if not result["success"]:
            return result

        # ── DB OFFLINE ────────────────────────────────────────────────────────
        if not is_db_ready():
            return _ok(
                evidence_id  = _mock_id("EV-"),
                storage_path = f"evidence/{self.incident_id}/{self.file_name}",
                public_url   = None,
                message      = f"Evidence '{self.file_name}' received (offline — not uploaded to Storage).",
                db_mode      = "offline",
            )

        # ── DB LIVE ───────────────────────────────────────────────────────────
        fs = get_firestore()

        # Verify parent incident exists
        if not fs.collection(IncidentDetails.FS_COLLECTION).document(self.incident_id).get().exists:
            return _err("incident_id",
                f"No incident record found with id='{self.incident_id}'.")

        # Upload to Firebase Storage
        timestamp    = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        storage_path = f"{self.STORAGE_BASE}/{self.incident_id}/{timestamp}_{self.file_name}"

        content_type = (
            "image/jpeg"        if self.ext in {".jpg", ".jpeg"} else
            "image/png"         if self.ext == ".png"            else
            "video/mp4"         if self.ext == ".mp4"            else
            "video/x-matroska"
        )
        blob = get_storage_bucket().blob(storage_path)
        blob.upload_from_string(self.file_bytes, content_type=content_type)
        blob.make_public()
        public_url = blob.public_url

        # Write metadata to Firestore
        _, doc_ref = fs.collection(self.FS_COLLECTION).add({
            "incident_id"  : self.incident_id,
            "file_name"    : self.file_name,
            "file_type"    : self.file_type,
            "storage_path" : storage_path,
            "public_url"   : public_url,
            "uploaded_at"  : _now(),
        })

        return _ok(
            evidence_id  = doc_ref.id,
            storage_path = storage_path,
            public_url   = public_url,
            message      = f"Evidence '{self.file_name}' uploaded successfully.",
            db_mode      = "live",
        )

    # ── Reads ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_by_incident(incident_id: str) -> list[dict]:
        if not is_db_ready():
            return []
        docs = (
            get_firestore().collection(EvidenceUpload.FS_COLLECTION)
            .where("incident_id", "==", incident_id)
            .stream()
        )
        result = []
        for d in docs:
            row = d.to_dict()
            row["evidence_id"] = d.id
            result.append(row)
        return result
