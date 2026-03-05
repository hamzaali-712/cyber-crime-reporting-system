"""
CyberSecure – Flask REST API  |  Firebase Firestore Edition

Run
---
  pip install firebase-admin flask flask-cors
  python app.py

Environment
-----------
  GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json   (default)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from models import (
    PersonalInformation,
    IncidentDetails,
    EvidenceUpload,
    PAKISTAN_CITIES,
    CRIME_CATEGORIES,
)

app = Flask(__name__)
CORS(app)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def bad(message: str, field: str = "", status: int = 400):
    return jsonify({"success": False, "field": field, "message": message}), status

def ok(data: dict, status: int = 200):
    return jsonify({"success": True, **data}), status


# ─────────────────────────────────────────────
# Lookup endpoints
# ─────────────────────────────────────────────

@app.get("/api/cities")
def get_cities():
    """Return all valid Pakistani cities."""
    return ok({"cities": PAKISTAN_CITIES})


@app.get("/api/crime-categories")
def get_crime_categories():
    """Return all valid crime categories."""
    return ok({"categories": CRIME_CATEGORIES})


# ─────────────────────────────────────────────
# Class 1 – Personal Information
# ─────────────────────────────────────────────

@app.post("/api/personal-information")
def create_personal_information():
    """
    POST /api/personal-information
    Content-Type: application/json

    Body:
        full_name   string  required
        cnic        string  required   e.g. 42301-1234567-1
        gender      string  required   Male | Female | Other
        mobile      string  required   e.g. +923001234567
        email       string  optional
        occupation  string  optional

    Returns:
        201 { success, personal_id, message }
        400 { success, field, message }          – validation error
        409 { success, field, message }          – duplicate CNIC
    """
    data = request.get_json(silent=True) or {}

    person = PersonalInformation(
        full_name  = data.get("full_name", ""),
        cnic       = data.get("cnic", ""),
        gender     = data.get("gender", ""),
        mobile     = data.get("mobile", ""),
        email      = data.get("email", ""),
        occupation = data.get("occupation", ""),
    )

    result = person.save()
    if not result["success"]:
        status = 409 if result.get("field") == "cnic" else 400
        return jsonify(result), status

    return ok(result, 201)


@app.get("/api/personal-information/<string:cnic>")
def get_personal_information(cnic: str):
    record = PersonalInformation.get_by_id(cnic)
    if not record:
        return bad(f"No record found for CNIC '{cnic}'.", status=404)
    return ok({"record": record})


# ─────────────────────────────────────────────
# Class 2 – Incident Details
# ─────────────────────────────────────────────

@app.post("/api/incident-details")
def create_incident_details():
    """
    POST /api/incident-details
    Content-Type: application/json

    Body:
        personal_id     string  required   (CNIC of the person)
        city            string  required
        crime_category  string  required
        crime_details   string  required   max 3500 chars
        postal_address  string  optional

    Returns:
        201 { success, incident_id, message }
        400 { success, field, message }
    """
    data = request.get_json(silent=True) or {}

    personal_id = data.get("personal_id", "").strip()
    if not personal_id:
        return bad("personal_id (CNIC) is required.", "personal_id")

    incident = IncidentDetails(
        personal_id    = personal_id,
        city           = data.get("city", ""),
        crime_category = data.get("crime_category", ""),
        crime_details  = data.get("crime_details", ""),
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


# ─────────────────────────────────────────────
# Class 3 – Evidence Upload
# ─────────────────────────────────────────────

@app.post("/api/evidence-upload")
def upload_evidence():
    """
    POST /api/evidence-upload
    Content-Type: multipart/form-data

    Fields:
        incident_id   form field  required
        files[]       file(s)     optional  PNG | JPG | MP4 | MKV, total ≤ 500 MB

    Returns:
        201 { success, results[] }
        400 { success, field, message }
    """
    incident_id = request.form.get("incident_id", "").strip()
    if not incident_id:
        return bad("incident_id is required.", "incident_id")

    files = request.files.getlist("files[]")
    real_files = [f for f in files if f.filename != ""]

    # Evidence is optional
    if not real_files:
        return ok({"message": "No files provided – evidence upload skipped.", "results": []})

    # Enforce 500 MB total
    raw_bytes = [(f, f.read()) for f in real_files]
    total = sum(len(b) for _, b in raw_bytes)
    if total > EvidenceUpload.MAX_TOTAL_BYTES:
        return bad(
            f"Total upload size exceeds 500 MB ({total // (1024 * 1024)} MB sent).",
            "files"
        )

    results = []
    for uploaded_file, content in raw_bytes:
        ev = EvidenceUpload(
            incident_id = incident_id,
            file_name   = uploaded_file.filename,
            file_bytes  = content,
        )
        results.append(ev.save())

    all_ok = all(r["success"] for r in results)
    return jsonify({"success": all_ok, "results": results}), (201 if all_ok else 207)


@app.get("/api/evidence-upload/<string:incident_id>")
def get_evidence(incident_id: str):
    records = EvidenceUpload.get_by_incident(incident_id)
    return ok({"incident_id": incident_id, "evidence": records})


# ─────────────────────────────────────────────
# Convenience – full complaint in one request
# ─────────────────────────────────────────────

@app.post("/api/submit-complaint")
def submit_complaint():
    """
    POST /api/submit-complaint
    Content-Type: multipart/form-data

    Send all personal + incident fields as flat form fields,
    plus optional files[] for evidence.

    Returns:
        201 { success, personal_id, incident_id, evidence_count, evidence[], message }
    """
    # ── Step 1: Personal Information ────────────────────────────
    person = PersonalInformation(
        full_name  = request.form.get("full_name", ""),
        cnic       = request.form.get("cnic", ""),
        gender     = request.form.get("gender", ""),
        mobile     = request.form.get("mobile", ""),
        email      = request.form.get("email", ""),
        occupation = request.form.get("occupation", ""),
    )
    p_result = person.save()
    if not p_result["success"]:
        status = 409 if p_result.get("field") == "cnic" else 400
        return jsonify(p_result), status

    personal_id = p_result["personal_id"]   # this is the CNIC

    # ── Step 2: Incident Details ─────────────────────────────────
    incident = IncidentDetails(
        personal_id    = personal_id,
        postal_address = request.form.get("postal_address", ""),
        city           = request.form.get("city", ""),
        crime_category = request.form.get("crime_category", ""),
        crime_details  = request.form.get("crime_details", ""),
    )
    i_result = incident.save()
    if not i_result["success"]:
        return jsonify(i_result), 400

    incident_id = i_result["incident_id"]

    # ── Step 3: Evidence (optional) ──────────────────────────────
    evidence_results = []
    for uploaded_file in request.files.getlist("files[]"):
        if uploaded_file.filename == "":
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
    }, 201)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
