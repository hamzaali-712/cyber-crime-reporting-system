"""
CyberSecure – Firebase Configuration
======================================
Controls whether Firebase is active or offline (mock mode).

HOW TO SWITCH DATABASE ON / OFF
────────────────────────────────
Option 1 – Edit the flag below (simplest):
    DB_ENABLED = True    ← Firebase is live
    DB_ENABLED = False   ← No Firebase; app still runs with mock responses

Option 2 – Environment variable (overrides the flag):
    set DB_ENABLED=true      (Windows CMD)
    export DB_ENABLED=true   (Mac / Linux)

HOW TO CONNECT YOUR FIREBASE PROJECT
──────────────────────────────────────
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key" → save file as  serviceAccountKey.json
   (put it in the same folder as this file)
3. Fill in your RTDB URL and Storage bucket in FIREBASE_CONFIG below
4. Set  DB_ENABLED = True  (or env var)
5. Run:
       pip install -r requirements.txt
       python app.py
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("cybersecure.firebase")

# ──────────────────────────────────────────────────────────────
# ✏️  STEP 1 – FLIP THIS FLAG
#     True  = try to connect Firebase
#     False = run offline / mock mode (no Firebase needed)
# ──────────────────────────────────────────────────────────────
DB_ENABLED: bool = os.environ.get("DB_ENABLED", "false").lower() in ("true", "1", "yes")

# ──────────────────────────────────────────────────────────────
# ✏️  STEP 2 – FILL IN YOUR FIREBASE PROJECT VALUES
# ──────────────────────────────────────────────────────────────
FIREBASE_CONFIG = {
    # Path to your downloaded service-account JSON key file
    "service_account_key": os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json"
    ),

    # Realtime Database URL
    # Firebase Console → Realtime Database → copy the URL shown at the top
    # Format: https://<your-project-id>-default-rtdb.firebaseio.com
    "rtdb_url": os.environ.get(
        "FIREBASE_RTDB_URL",
        "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com"   # ← EDIT THIS
    ),

    # Storage bucket name
    # Firebase Console → Storage → copy the bucket name (without gs://)
    # Format: your-project-id.appspot.com
    "storage_bucket": os.environ.get(
        "FIREBASE_STORAGE_BUCKET",
        "YOUR-PROJECT-ID.appspot.com"                           # ← EDIT THIS
    ),
}
# ──────────────────────────────────────────────────────────────


# ── Internal Firebase state ────────────────────────────────────────────────────
_firestore_client = None
_rtdb_ref          = None
_storage_bucket    = None
_firebase_ready    = False


def _init_firebase() -> bool:
    """
    Try to initialise Firebase Admin SDK.
    Returns True on success, False on any failure.
    The rest of the app continues working either way.
    """
    global _firestore_client, _rtdb_ref, _storage_bucket, _firebase_ready

    if not DB_ENABLED:
        log.warning("DB_ENABLED=False — Firebase is OFFLINE. App runs in mock mode.")
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, db as rtdb, storage

        if not firebase_admin._apps:
            key_path = FIREBASE_CONFIG["service_account_key"]
            if not os.path.isfile(key_path):
                raise FileNotFoundError(
                    f"Service account key not found at '{key_path}'. "
                    f"Download it from Firebase Console → Project Settings → Service Accounts."
                )
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred, {
                "databaseURL"   : FIREBASE_CONFIG["rtdb_url"],
                "storageBucket" : FIREBASE_CONFIG["storage_bucket"],
            })

        _firestore_client = firestore.client()
        _rtdb_ref          = rtdb.reference("/")
        _storage_bucket    = storage.bucket()
        _firebase_ready    = True
        log.info("✅  Firebase CONNECTED  — Firestore + RTDB + Storage are active.")
        return True

    except FileNotFoundError as exc:
        log.error("❌  Firebase init failed — %s", exc)
    except Exception as exc:
        log.error("❌  Firebase init failed — %s: %s", type(exc).__name__, exc)

    log.warning("⚠️   Continuing in OFFLINE / mock mode.")
    return False


# Run on import
_init_firebase()


# ── Public accessors ──────────────────────────────────────────────────────────

def is_db_ready() -> bool:
    """Return True only when Firebase is enabled AND successfully connected."""
    return _firebase_ready


def get_firestore():
    return _firestore_client


def get_rtdb():
    return _rtdb_ref


def get_storage_bucket():
    return _storage_bucket


def db_status() -> dict:
    """Status dict for the /api/health endpoint."""
    return {
        "db_enabled"   : DB_ENABLED,
        "db_connected" : _firebase_ready,
        "mode"         : "live" if _firebase_ready else "offline",
        "services"     : {
            "firestore" : _firestore_client is not None,
            "rtdb"      : _rtdb_ref         is not None,
            "storage"   : _storage_bucket   is not None,
        },
    }
