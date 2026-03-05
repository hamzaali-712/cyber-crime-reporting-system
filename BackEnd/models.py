"""
CyberSecure – Cyber Crime Reporting Portal
Backend Models  |  Firebase Firestore Edition

Collections
-----------
  personal_information  – one document per complaint, CNIC as unique key
  incident_details      – one document per incident, linked by personal_id
  evidence_uploads      – one document per file, linked by incident_id

Prerequisites
-------------
  pip install firebase-admin flask flask-cors

Place your Firebase service account JSON file at:
  serviceAccountKey.json   (same folder as this file)
Or set the env var:
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

# ─────────────────────────────────────────────
# Firebase initialisation (runs once on import)
# ─────────────────────────────────────────────

_SA_KEY = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(_SA_KEY)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Upload directory for evidence files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _err(field: str, msg: str) -> dict:
    return {"success": False, "field": field, "message": msg}

def _ok(**kwargs) -> dict:
    return {"success": True, **kwargs}


# ─────────────────────────────────────────────
# Class 1 – Personal Information
# ─────────────────────────────────────────────

class PersonalInformation:
    """
    Validates and saves personal information to Firestore.

    Firestore Collection : personal_information
    Document ID          : CNIC (ensures global uniqueness at the DB level too)

    Fields
    ------
    full_name   : str  – required, 2–100 chars
    cnic        : str  – required, format 12345-1234567-1
    gender      : str  – required  → Male | Female | Other
    mobile      : str  – required  → +92XXXXXXXXXX (10 digits after +92)
    email       : str  – optional, must contain @ when provided
    occupation  : str  – optional
    """

    COLLECTION = "personal_information"
    GENDERS    = {"Male", "Female", "Other"}
    CNIC_RE    = re.compile(r"^\d{5}-\d{7}-\d$")
    MOBILE_RE  = re.compile(r"^\+92[0-9]{10}$")

    def __init__(self, full_name: str, cnic: str, gender: str,
                 mobile: str, email: str = "", occupation: str = ""):
        self.full_name  = full_name.strip()
        self.cnic       = cnic.strip()
        self.gender     = gender.strip()
        self.mobile     = mobile.strip()
        self.email      = email.strip()
        self.occupation = occupation.strip()

    # ── Validation ──────────────────────────────────────────────────────────

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

    # ── Firestore operations ─────────────────────────────────────────────────

    def _cnic_exists(self) -> bool:
        """Check Firestore for an existing document with this CNIC."""
        doc = db.collection(self.COLLECTION).document(self.cnic).get()
        return doc.exists

    def save(self) -> dict:
        """Validate then write to Firestore. Uses CNIC as document ID."""
        result = self.validate()
        if not result["success"]:
            return result

        # Duplicate CNIC check
        if self._cnic_exists():
            return _err("cnic",
                        f"A complaint with CNIC {self.cnic} already exists in the system. "
                        "Please contact support if you believe this is an error.")

        payload = {
            "full_name"  : self.full_name,
            "cnic"       : self.cnic,
            "gender"     : self.gender,
            "mobile"     : self.mobile,
            "email"      : self.email   or None,
            "occupation" : self.occupation or None,
            "created_at" : _now(),
        }

        db.collection(self.COLLECTION).document(self.cnic).set(payload)

        return _ok(
            personal_id=self.cnic,
            message="Personal information saved successfully.",
        )

    @staticmethod
    def get_by_id(cnic: str) -> dict | None:
        doc = db.collection(PersonalInformation.COLLECTION).document(cnic).get()
        return doc.to_dict() if doc.exists else None


# ─────────────────────────────────────────────
# Class 2 – Incident Details
# ─────────────────────────────────────────────

class IncidentDetails:
    """
    Validates and saves incident details to Firestore.

    Firestore Collection : incident_details
    Document ID          : auto-generated by Firestore

    Fields
    ------
    personal_id     : str  – CNIC / doc-id of the parent personal_information record
    postal_address  : str  – optional
    city            : str  – required, must be a valid Pakistani city
    crime_category  : str  – required, from predefined list
    crime_details   : str  – required, max 3500 characters
    """

    COLLECTION      = "incident_details"
    MAX_DETAILS_LEN = 3500

    def __init__(self, personal_id: str, city: str, crime_category: str,
                 crime_details: str, postal_address: str = ""):
        self.personal_id    = personal_id
        self.postal_address = postal_address.strip()
        self.city           = city.strip()
        self.crime_category = crime_category.strip()
        self.crime_details  = crime_details.strip()

    # ── Validation ──────────────────────────────────────────────────────────

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
        if len(self.crime_details) > self.MAX_DETAILS_LEN:
            return _err("crime_details",
                        f"Crime details must not exceed {self.MAX_DETAILS_LEN} characters "
                        f"(currently {len(self.crime_details)}).")

        return {"success": True}

    # ── Firestore operations ─────────────────────────────────────────────────

    def save(self) -> dict:
        result = self.validate()
        if not result["success"]:
            return result

        # Verify the parent personal record exists
        parent = db.collection(PersonalInformation.COLLECTION).document(self.personal_id).get()
        if not parent.exists:
            return _err("personal_id",
                        f"No personal information record found for CNIC '{self.personal_id}'.")

        payload = {
            "personal_id"    : self.personal_id,
            "postal_address" : self.postal_address or None,
            "city"           : self.city,
            "crime_category" : self.crime_category,
            "crime_details"  : self.crime_details,
            "created_at"     : _now(),
        }

        # Auto-generate document ID
        _, doc_ref = db.collection(self.COLLECTION).add(payload)

        return _ok(
            incident_id=doc_ref.id,
            message="Incident details saved successfully.",
        )

    @staticmethod
    def get_by_id(incident_id: str) -> dict | None:
        doc = db.collection(IncidentDetails.COLLECTION).document(incident_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["incident_id"] = doc.id
        return data

    @staticmethod
    def get_by_personal_id(personal_id: str) -> list[dict]:
        docs = (
            db.collection(IncidentDetails.COLLECTION)
            .where("personal_id", "==", personal_id)
            .stream()
        )
        result = []
        for d in docs:
            row = d.to_dict()
            row["incident_id"] = d.id
            result.append(row)
        return result


# ─────────────────────────────────────────────
# Class 3 – Evidence Upload
# ─────────────────────────────────────────────

class EvidenceUpload:
    """
    Handles optional evidence uploads linked to an incident.

    Firestore Collection : evidence_uploads
    Storage              : local 'uploads/' folder (swap for Firebase Storage if needed)

    Accepted file types  : PNG, JPG/JPEG, MP4, MKV
    Max total size       : 500 MB (enforced in the API layer)
    """

    COLLECTION         = "evidence_uploads"
    ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
    ALLOWED_VIDEO_EXTS = {".mp4", ".mkv"}
    ALLOWED_EXTS       = ALLOWED_IMAGE_EXTS | ALLOWED_VIDEO_EXTS
    MAX_TOTAL_BYTES    = 500 * 1024 * 1024   # 500 MB

    def __init__(self, incident_id: str, file_name: str,
                 file_bytes: bytes, file_type: str = ""):
        self.incident_id = incident_id
        self.file_name   = Path(file_name).name          # strip path traversal
        self.file_bytes  = file_bytes
        self.ext         = Path(self.file_name).suffix.lower()
        self.file_type   = file_type or (
            "image" if self.ext in self.ALLOWED_IMAGE_EXTS else "video"
        )

    # ── Validation ──────────────────────────────────────────────────────────

    def validate(self) -> dict:
        if not self.file_name:
            return _err("file", "File name cannot be empty.")
        if self.ext not in self.ALLOWED_EXTS:
            return _err("file",
                        f"File type '{self.ext}' is not allowed. "
                        "Accepted: PNG, JPG, MP4, MKV.")
        if len(self.file_bytes) == 0:
            return _err("file", "Uploaded file is empty.")
        return {"success": True}

    # ── Firestore + local storage operations ────────────────────────────────

    def save(self) -> dict:
        result = self.validate()
        if not result["success"]:
            return result

        # Verify parent incident exists
        parent = db.collection(IncidentDetails.COLLECTION).document(self.incident_id).get()
        if not parent.exists:
            return _err("incident_id",
                        f"No incident record found with id='{self.incident_id}'.")

        # Write file to disk
        timestamp  = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        safe_name  = f"{self.incident_id}_{timestamp}_{self.file_name}"
        file_path  = UPLOAD_DIR / safe_name
        file_path.write_bytes(self.file_bytes)

        # Save metadata to Firestore
        payload = {
            "incident_id" : self.incident_id,
            "file_name"   : self.file_name,
            "file_type"   : self.file_type,
            "file_path"   : str(file_path),
            "uploaded_at" : _now(),
        }
        _, doc_ref = db.collection(self.COLLECTION).add(payload)

        return _ok(
            evidence_id=doc_ref.id,
            file_path=str(file_path),
            message=f"Evidence '{self.file_name}' uploaded successfully.",
        )

    @staticmethod
    def get_by_incident(incident_id: str) -> list[dict]:
        docs = (
            db.collection(EvidenceUpload.COLLECTION)
            .where("incident_id", "==", incident_id)
            .stream()
        )
        result = []
        for d in docs:
            row = d.to_dict()
            row["evidence_id"] = d.id
            result.append(row)
        return result
