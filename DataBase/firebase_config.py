"""
CyberSecure – Firebase Configuration
=====================================
Initialises all three Firebase services:
  • Firestore          – structured complaint data
  • Realtime Database  – live complaint status tracking
  • Firebase Storage   – evidence file storage

Setup
-----
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key" → save as  serviceAccountKey.json
3. Copy your project values into the CONFIG block below
4. Run:  pip install -r requirements.txt
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, db as rtdb, storage

# ─────────────────────────────────────────────────────────────
# ✏️  EDIT THESE VALUES  (from your Firebase Console)
# ─────────────────────────────────────────────────────────────
CONFIG = {
    # Path to your downloaded service-account JSON key
    "service_account_key": os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json"
    ),

    # Realtime Database URL  →  Firebase Console → Realtime Database → Copy URL
    # Format: https://<your-project-id>-default-rtdb.firebaseio.com
    "rtdb_url": os.environ.get(
        "FIREBASE_RTDB_URL", "https://your-project-id-default-rtdb.firebaseio.com"
    ),

    # Storage bucket  →  Firebase Console → Storage → Copy bucket name
    # Format: your-project-id.appspot.com
    "storage_bucket": os.environ.get(
        "FIREBASE_STORAGE_BUCKET", "your-project-id.appspot.com"
    ),
}
# ─────────────────────────────────────────────────────────────


def init_firebase():
    """Initialise Firebase app (safe to call multiple times)."""
    if firebase_admin._apps:
        return  # already initialised

    cred = credentials.Certificate(CONFIG["service_account_key"])
    firebase_admin.initialize_app(cred, {
        "databaseURL"   : CONFIG["rtdb_url"],
        "storageBucket" : CONFIG["storage_bucket"],
    })


# Initialise on import
init_firebase()


def get_firestore():
    """Return Firestore client."""
    return firestore.client()


def get_rtdb():
    """Return Realtime Database root reference."""
    return rtdb.reference("/")


def get_storage_bucket():
    """Return the default Storage bucket."""
    return storage.bucket()
