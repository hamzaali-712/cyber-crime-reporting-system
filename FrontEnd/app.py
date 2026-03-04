"""
CyberSecure – Flask REST API
=============================
Connects the HTML frontend to the three backend model classes.

Run
────
    pip install -r requirements.txt
    python app.py

The server starts on  http://localhost:5000
Open  cybersecure.html  in your browser — the form will POST to this server.

DB modes
─────────
  offline (default) : app runs, validates, returns mock IDs — no Firebase needed
  live              : set DB_ENABLED=true in firebase_config.py + add serviceAccountKey.json
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from firebase_config import db_status
from models import (
    PersonalInformation,
    IncidentDetails,
    EvidenceUpload,
    PAKISTAN_CITIES,
    CRIME_CATEGORIES,
    COMPLAINT_STATUSES,
)

app = Flask(__name__)

# ── CORS: allow the HTML file to call this API from any origin ─────────────────
# When you deploy, replace "*" with your actual frontend domain.
CORS(app, resources={r"/api/*": {"origins": "*"}})


# ─────────────────────────────────────────────────────────────
# Response helpers
# ─────────────────────────────────────────────────────────────

def bad(message: str, field: str = "", status: int = 400):
    return jsonify({"success": False, "field": field, "message": message}), status

def ok(data: dict, status: int = 200):
    return jsonify({"success": True, **data}), status


# ─────────────────────────────────────────────────────────────
# Health check  – frontend calls this on page load
# ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    """
    GET /api/health
    Returns server + database status.
    The frontend uses this to show a "DB connected" badge.
    """
    return ok({"server": "online", "database": db_status()})


# ─────────────────────────────────────────────────────────────
# Lookup endpoints  (populate dropdowns in the HTML)
# ─────────────────────────────────────────────────────────────

@app.get("/api/cities")
def get_cities():
    return ok({"cities": PAKISTAN_CITIES})


@app.get("/api/crime-categories")
def get_crime_categories():
    return ok({"categories": CRIME_CATEGORIES})


@app.get("/api/complaint-statuses")
def get_statuses():
    return ok({"statuses": COMPLAINT_STATUSES})


# ─────────────────────────────────────────────────────────────
# Class 1 – Personal Information
# ─────────────────────────────────────────────────────────────

@app.post("/api/personal-information")
def create_personal_information():
    """
    POST /api/personal-information
    Content-Type: application/json

    Body:
        full_name*    string
        cnic*         string   e.g. "42301-1234567-1"
        gender*       string   "Male" | "Female" | "Other"
        mobile*       string   e.g. "+923001234567"
        email         string   optional
        occupation    string   optional

    Returns 201 on success, 400 on validation error, 409 on duplicate CNIC.
    """
    data = request.get_json(silent=True) or {}
    person = PersonalInformation(
        full_name  = data.get("full_name",  ""),
        cnic       = data.get("cnic",       ""),
        gender     = data.get("gender",     ""),
        mobile     = data.get("mobile",     ""),
        email      = data.get("email",      ""),
        occupation = data.get("occupation", ""),
    )
    result = person.save()
    if not result["success"]:
        return jsonify(result), (409 if result.get("field") == "cnic" else 400)
    return ok(result, 201)


@app.get("/api/personal-information/<string:cnic>")
def get_personal_information(cnic: str):
    record = PersonalInformation.get_by_id(cnic)
    if not record:
        return bad(f"No record found for CNIC '{cnic}'.", status=404)
    return ok({"record": record})


@app.get("/api/complaint-status/<string:cnic>")
def get_complaint_status(cnic: str):
    status = PersonalInformation.get_status(cnic)
    if not status:
        return bad(f"No status found for CNIC '{cnic}'.", status=404)
    return ok({"cnic": cnic, "status_info": status})


@app.patch("/api/complaint-status/<string:cnic>")
def update_complaint_status(cnic: str):
    data       = request.get_json(silent=True) or {}
    new_status = data.get("status", "").strip()
    if not new_status:
        return bad("'status' field is required.", "status")
    result = PersonalInformation.update_status(cnic, new_status)
    return (ok(result) if result["success"] else (jsonify(result), 400))


# ─────────────────────────────────────────────────────────────
# Class 2 – Incident Details
# ─────────────────────────────────────────────────────────────

@app.post("/api/incident-details")
def create_incident_details():
    """
    POST /api/incident-details
    Content-Type: application/json

    Body:
        personal_id*      CNIC string
        city*             string
        crime_category*   string
        crime_details*    string  max 3500 chars
        postal_address    string  optional
    """
    data        = request.get_json(silent=True) or {}
    personal_id = data.get("personal_id", "").strip()
    if not personal_id:
        return bad("personal_id (CNIC) is required.", "personal_id")

    incident = IncidentDetails(
        personal_id    = personal_id,
        city           = data.get("city",           ""),
        crime_category = data.get("crime_category", ""),
        crime_details  = data.get("crime_details",  ""),
        postal_address = data.get("postal_address", ""),
    )
    result = incident.save()
    if not result["success"]:
        return jsonify(result), 400
    return ok(result, 201)


@app.get("/api/incident-details/<string:incident_id>")
def get_incident_details(incident_id: str):
    record = IncidentDetails.get_by_id(incident_id)
    if not record:
        return bad(f"No incident found with id='{incident_id}'.", status=404)
    return ok({"record": record})


@app.get("/api/incident-details/by-cnic/<string:cnic>")
def get_incidents_by_cnic(cnic: str):
    records = IncidentDetails.get_by_personal_id(cnic)
    return ok({"personal_id": cnic, "incidents": records})


# ─────────────────────────────────────────────────────────────
# Class 3 – Evidence Upload
# ─────────────────────────────────────────────────────────────

@app.post("/api/evidence-upload")
def upload_evidence():
    """
    POST /api/evidence-upload
    Content-Type: multipart/form-data

    Fields:
        incident_id*   text field
        files[]        file(s)  PNG | JPG | MP4 | MKV  (optional)
    Max total: 500 MB
    """
    incident_id = request.form.get("incident_id", "").strip()
    if not incident_id:
        return bad("incident_id is required.", "incident_id")

    files = [f for f in request.files.getlist("files[]") if f.filename]
    if not files:
        return ok({"message": "No files provided – evidence upload skipped.", "results": []})

    raw = [(f, f.read()) for f in files]
    if sum(len(b) for _, b in raw) > EvidenceUpload.MAX_TOTAL_BYTES:
        total_mb = sum(len(b) for _, b in raw) // (1024 * 1024)
        return bad(f"Total upload size exceeds 500 MB ({total_mb} MB sent).", "files")

    results = [
        EvidenceUpload(incident_id=incident_id, file_name=f.filename, file_bytes=b).save()
        for f, b in raw
    ]
    all_ok = all(r["success"] for r in results)
    return jsonify({"success": all_ok, "results": results}), (201 if all_ok else 207)


@app.get("/api/evidence-upload/<string:incident_id>")
def get_evidence(incident_id: str):
    return ok({"incident_id": incident_id, "evidence": EvidenceUpload.get_by_incident(incident_id)})


# ─────────────────────────────────────────────────────────────
# ★  MAIN ENDPOINT – Full complaint in one request
#    This is what cybersecure.html  POSTs to
# ─────────────────────────────────────────────────────────────

@app.post("/api/submit-complaint")
def submit_complaint():
    """
    POST /api/submit-complaint
    Content-Type: multipart/form-data

    Flat form fields (personal + incident) + optional files[].

    Flow:
        1. PersonalInformation.save()  → returns personal_id (CNIC)
        2. IncidentDetails.save()      → returns incident_id
        3. EvidenceUpload.save()       → one call per file (optional)

    Returns 201 on full success.
    Returns 400 / 409 on first failure, so the frontend knows exactly which
    field caused the error and can highlight it.
    """
    # ── Step 1: Personal Information ──────────────────────────────────────────
    person = PersonalInformation(
        full_name  = request.form.get("full_name",  ""),
        cnic       = request.form.get("cnic",       ""),
        gender     = request.form.get("gender",     ""),
        mobile     = request.form.get("mobile",     ""),
        email      = request.form.get("email",      ""),
        occupation = request.form.get("occupation", ""),
    )
    p_result = person.save()
    if not p_result["success"]:
        return jsonify(p_result), (409 if p_result.get("field") == "cnic" else 400)

    personal_id = p_result["personal_id"]   # = CNIC

    # ── Step 2: Incident Details ───────────────────────────────────────────────
    incident = IncidentDetails(
        personal_id    = personal_id,
        postal_address = request.form.get("postal_address", ""),
        city           = request.form.get("city",           ""),
        crime_category = request.form.get("crime_category", ""),
        crime_details  = request.form.get("crime_details",  ""),
    )
    i_result = incident.save()
    if not i_result["success"]:
        return jsonify(i_result), 400

    incident_id = i_result["incident_id"]

    # ── Step 3: Evidence (optional) ───────────────────────────────────────────
    evidence_results = []
    for uploaded_file in request.files.getlist("files[]"):
        if not uploaded_file.filename:
            continue
        ev = EvidenceUpload(
            incident_id = incident_id,
            file_name   = uploaded_file.filename,
            file_bytes  = uploaded_file.read(),
        )
        evidence_results.append(ev.save())

    return ok({
        "message"        : "Complaint submitted successfully.",
        "personal_id"    : personal_id,
        "incident_id"    : incident_id,
        "evidence_count" : len(evidence_results),
        "evidence"       : evidence_results,
        "db_mode"        : p_result.get("db_mode", "unknown"),
    }, 201)


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
