"""
Cybercrime Complaint Report Form Page
Modern Premium Version with Evidence Persistence
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid
import json

# Ensure local path imports work
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv()
logger = logging.getLogger(__name__)

# Paths
COMPLAINTS_FILE = ROOT_DIR / "backend" / "data" / "complaints.json"
EVIDENCE_DIR = ROOT_DIR / "backend" / "data" / "evidence"

def load_complaints():
    if os.path.exists(COMPLAINTS_FILE):
        try:
            with open(COMPLAINTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_complaints(complaints):
    os.makedirs(COMPLAINTS_FILE.parent, exist_ok=True)
    with open(COMPLAINTS_FILE, 'w') as f:
        json.dump(complaints, f, indent=2, default=str)

def save_evidence(tracking_id, uploaded_files):
    """Saves evidence files to the local filesystem."""
    if not uploaded_files:
        return []
    
    case_evidence_dir = EVIDENCE_DIR / tracking_id
    os.makedirs(case_evidence_dir, exist_ok=True)
    
    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = case_evidence_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(uploaded_file.name)
    
    return saved_files

def render_report_form(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Initialize Report", page_icon="📋", layout="wide")
    
    # ── Success/Result Display Area ──
    if 'last_tracking_id' not in st.session_state:
        st.session_state.last_tracking_id = None

    # ── Success View ──
    if st.session_state.last_tracking_id:
        success_html = f"""
<div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; padding: 2.5rem; border-radius: 20px; margin: 2rem 0; text-align: center; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 10px 40px rgba(0,0,0,0.4);">
    <div style="font-size: 4rem; margin-bottom: 1rem;">🛡️</div>
    <h1 style="color: #10b981; margin-top: 0; font-weight: 800; letter-spacing: -1px;">REPORT SECURED</h1>
    <p style="font-size: 1.25rem; color: #f8fafc; opacity: 0.9;">Your case has been successfully registered in the National Cyber Database.</p>
    <div style="background: #0f172a; padding: 2rem; border-radius: 15px; margin: 2rem 0; border: 1px solid #3b82f6; box-shadow: inset 0 0 20px rgba(59, 130, 246, 0.1);">
        <p style="color: #3b82f6; margin-bottom: 0.75rem; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; font-weight: 700;">OFFICIAL TRACKING ID</p>
        <h1 style="color: #ffffff; font-family: 'JetBrains Mono', monospace; margin: 0; font-size: 2.5rem; letter-spacing: 4px;">{st.session_state.last_tracking_id}</h1>
    </div>
    <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 1rem;">
        <p style="color: #94a3b8; font-size: 0.95rem; max-width: 500px;">
            <b>Pro Tip:</b> Save this ID now. You will need it to track your investigation status or provide additional evidence later.
        </p>
    </div>
</div>
""".replace("\n", " ")
        st.markdown(success_html, unsafe_allow_html=True)



        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("➕ FILE NEW COMPLAINT", use_container_width=True, type="primary"):
                st.session_state.last_tracking_id = None
                st.rerun()
            if st.button("📍 TRACK THIS CASE", use_container_width=True):
                # We could potentially auto-navigate to tracking, but for now let's just stay here
                # or set current_page to tracking if we have access to it.
                if 'current_page' in st.session_state:
                    st.session_state.current_page = "tracking"
                    st.rerun()
        return

    # ── Form View ──
    with st.form("complaint_form", clear_on_submit=False):
        st.markdown('<div class="complaint-form">', unsafe_allow_html=True)

        st.markdown("### 👤 CONTACT INFORMATION")
        anonymous = st.checkbox("MAINTAIN OPERATIONAL ANONYMITY", value=False)
        email = st.text_input("PRIMARY EMAIL (REQUIRED)", placeholder="citizen@example.com")

        if not anonymous:
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("FULL LEGAL NAME")
                phone = st.text_input("MOBILE CONTACT")
            with c2:
                cnic = st.text_input("CNIC (13 DIGITS)", max_chars=13)
                address = st.text_area("PHYSICAL ADDRESS")
        else:
            full_name, phone, cnic, address = "ANONYMOUS", "N/A", "N/A", "N/A"

        st.markdown("---")
        st.markdown("### 🛰️ INCIDENT MATRIX")
        c_type, c_date = st.columns(2)
        with c_type:
            reason = st.selectbox("CRIME CLASSIFICATION", ["Hacking", "Phishing", "Cyberstalking", "Online Harassment", "Financial Fraud", "Other"])
        with c_date:
            inc_date = st.date_input("INCIDENT TIMESTAMP")
        
        location = st.text_input("LOCATION (URL/Physical)")
        description = st.text_area("DETAILED LOG", height=150)

        st.markdown("#### 📎 ELECTRONIC EVIDENCE BUNDLE")
        uploaded_files = st.file_uploader("UPLOAD DATA", accept_multiple_files=True, type=['jpg','png','pdf','mp4','zip'])

        submitted = st.form_submit_button("SUBMIT CASE REPORT", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if not email or "@" not in email:
            st.error("❌ CRITICAL ERROR: Valid Email Address is required for Case Registration.")
        elif len(description) < 20:
            st.error("❌ INSUFFICIENT DATA: Please provide a more detailed log of the incident (min 20 chars).")
        else:
            with st.spinner("INITIATING SECURE REGISTRATION..."):
                tracking_id = f"CCRS-PK-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
                
                # Save files
                evidence_filenames = save_evidence(tracking_id, uploaded_files)
                
                complaint_data = {
                    "tracking_id": tracking_id,
                    "email": email,
                    "full_name": full_name,
                    "phone": phone,
                    "cnic": cnic,
                    "address": address,
                    "anonymous": anonymous,
                    "incident_date": inc_date.isoformat(),
                    "location": location,
                    "complaint_reason": reason,
                    "description": description,
                    "evidence_files": evidence_filenames,
                    "submitted_at": datetime.now().isoformat(),
                    "status": "pending"
                }

                complaints = load_complaints()
                complaints[tracking_id] = complaint_data
                save_complaints(complaints)
                
                st.session_state.last_tracking_id = tracking_id
                st.balloons()
                st.rerun()



if __name__ == "__main__":
    render_report_form()
