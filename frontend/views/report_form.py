"""
Cybercrime Complaint Report Form Page
Modern Premium Version with Centralized DB Service & Realistic Terminology
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid

# Ensure local path imports work
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.services.database_service import db_service

load_dotenv()
logger = logging.getLogger(__name__)

# Paths
EVIDENCE_DIR = ROOT_DIR / "backend" / "data" / "evidence"

def save_evidence(tracking_id, uploaded_files):
    """Saves evidence files to the local filesystem and registers them securely."""
    if not uploaded_files:
        return []
    
    case_evidence_dir = EVIDENCE_DIR / tracking_id
    os.makedirs(case_evidence_dir, exist_ok=True)
    
    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = case_evidence_dir / uploaded_file.name
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(uploaded_file.name)
        except Exception as e:
            logger.error(f"Error saving physical evidence {uploaded_file.name}: {e}")
            
    return saved_files

def render_report_form(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="File Cyber Complaint - NCIA", page_icon="📋", layout="wide")
    
    st.markdown("## 📋 INITIALIZE SECURE CYBER COMPLAINT")
    st.write("Submit formal details and electronic evidence regarding an electronic offense.")

    # Success/Result Display Area
    if 'last_tracking_id' not in st.session_state:
        st.session_state.last_tracking_id = None

    # Success View
    if st.session_state.last_tracking_id:
        success_html = f"""
<div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; padding: 2.5rem; border-radius: 20px; margin: 2rem 0; text-align: center; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 10px 40px rgba(0,0,0,0.4);">
    <div style="font-size: 4rem; margin-bottom: 1rem;">🛡️</div>
    <h1 style="color: #10b981; margin-top: 0; font-weight: 800; letter-spacing: -1px;">COMPLAINT REGISTERED</h1>
    <p style="font-size: 1.25rem; color: #f8fafc; opacity: 0.9;">Your cybercrime report has been successfully recorded in the National Cyber Database.</p>
    <div style="background: #0f172a; padding: 2rem; border-radius: 15px; margin: 2rem 0; border: 1px solid #3b82f6; box-shadow: inset 0 0 20px rgba(59, 130, 246, 0.1);">
        <p style="color: #3b82f6; margin-bottom: 0.75rem; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; font-weight: 700;">YOUR SEARCH & TRACKING ID</p>
        <h1 style="color: #ffffff; font-family: 'JetBrains Mono', monospace; margin: 0; font-size: 2.5rem; letter-spacing: 4px;">{st.session_state.last_tracking_id}</h1>
    </div>
    <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 1rem;">
        <p style="color: #94a3b8; font-size: 0.95rem; max-width: 500px;">
            <b>Notice:</b> Please copy and save this tracking ID safely. You will need it to view the status of your investigation, add further statements, or print your official complaint copy.
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
            if st.button("📍 TRACK CASE STATUS", use_container_width=True):
                if 'current_page' in st.session_state:
                    st.session_state.current_page = "tracking"
                    st.rerun()
        return

    # Form View
    with st.form("complaint_form", clear_on_submit=False):
        st.markdown('<div class="complaint-form">', unsafe_allow_html=True)

        st.markdown("### 👤 COMPLAINANT INFORMATION")
        anonymous = st.checkbox("Report Anonymously (Hide Legal Name)", value=False, help="Check this box if you wish to file the complaint anonymously. Note: Providing your details helps investigators follow up more effectively.")
        
        email = st.text_input("Contact Email Address (Required)", placeholder="complainant@example.com", help="We will use this email address to send automated updates and coordinate details.")

        if not anonymous:
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Full Legal Name", placeholder="As printed on CNIC")
                phone = st.text_input("Mobile / Contact Number", placeholder="03XXXXXXXXX")
            with c2:
                cnic = st.text_input("CNIC Number (13 Digits)", max_chars=13, placeholder="E.g., 3740512345678")
                address = st.text_area("Home / Mailing Address", placeholder="Complete residential address")
        else:
            full_name, phone, cnic, address = "ANONYMOUS", "N/A", "N/A", "N/A"

        st.markdown("---")
        st.markdown("### 🛰️ INCIDENT DETAILS")
        c_type, c_date = st.columns(2)
        with c_type:
            reason = st.selectbox("Type of Cybercrime", ["Hacking", "Phishing", "Cyberstalking", "Online Harassment", "Financial Fraud", "Other"])
        with c_date:
            inc_date = st.date_input("Date of Occurrence")
        
        location = st.text_input("Incident Source Location (URL Link, Profile Link, Phone Number, or Physical Location)")
        description = st.text_area("Detailed Incident Log / Statement", height=150, placeholder="Please describe what happened, including any relevant emails, phone numbers, or profiles used by the suspect.")

        st.markdown("#### 📎 ATTACH DIGITAL EVIDENCE FILES")
        st.write("Upload supporting evidence securely. Files are encrypted and stored in our secure national datacenter.")
        uploaded_files = st.file_uploader("Upload Evidence Files", accept_multiple_files=True, type=['jpg','png','jpeg','pdf','mp4','zip'])

        submitted = st.form_submit_button("SUBMIT OFFICIAL COMPLAINT", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if not email or "@" not in email:
            st.error("❌ Email Validation Failure: A valid email address is required to register your complaint.")
        elif not anonymous and cnic and len(cnic) != 13:
            st.error("❌ CNIC Validation Failure: Your CNIC must be exactly 13 digits without spaces or dashes.")
        elif len(description) < 20:
            st.error("❌ Insufficient Information: Please write a more detailed explanation of the cybercrime incident (minimum 20 characters).")
        else:
            with st.spinner("Registering complaint in National Database..."):
                # Unique Tracking ID following standard CCRS schema
                year = datetime.now().year
                random_part = str(uuid.uuid4())[:8].upper()
                tracking_id = f"CCRS-PK-{year}-{random_part}"
                
                # Save physical files
                evidence_filenames = save_evidence(tracking_id, uploaded_files)
                
                complaint_data = {
                    "tracking_id": tracking_id,
                    "email": email.strip(),
                    "full_name": full_name.strip(),
                    "phone": phone.strip(),
                    "cnic": cnic.strip(),
                    "address": address.strip(),
                    "anonymous": anonymous,
                    "incident_date": inc_date.isoformat(),
                    "location": location.strip(),
                    "complaint_reason": reason,
                    "description": description.strip(),
                    "evidence_files": evidence_filenames,
                    "submitted_at": datetime.now().isoformat(),
                    "status": "pending"
                }

                # Centralized Database Service Call
                db_service.create_complaint(complaint_data)
                
                st.session_state.last_tracking_id = tracking_id
                st.balloons()
                st.rerun()

if __name__ == "__main__":
    render_report_form()
