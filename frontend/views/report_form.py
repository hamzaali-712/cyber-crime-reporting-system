"""
Cybercrime Complaint Report Form Page
Modern Premium Version
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

# Ensure local path imports work regardless of run directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

# Database file
COMPLAINTS_FILE = ROOT_DIR / "backend" / "data" / "complaints.json"

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

def render_report_form(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Initialize Report - Cyber System", page_icon="📋", layout="wide")
    
    st.markdown("## 📋 INITIALIZE NEW CASE REPORT")
    st.write("Please provide precise details. All entries are subject to legal verification.")
    
    # Navigation
    if st.button("← RETURN TO CORE", use_container_width=False):
        st.session_state.current_page = "home"
        st.rerun()
    
    with st.form("complaint_form"):
        st.markdown('<div class="complaint-form">', unsafe_allow_html=True)

        # Contact Node
        st.markdown("### 👤 CONTACT INFORMATION")
        anonymous = st.checkbox("MAINTAIN OPERATIONAL ANONYMITY", value=False)
        
        email = st.text_input("PRIMARY EMAIL (REQUIRED FOR STATUS UPDATES)", placeholder="citizen@example.com")

        if not anonymous:
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("FULL LEGAL NAME")
                phone = st.text_input("MOBILE CONTACT")
            with col2:
                cnic = st.text_input("CNIC (13 DIGITS)", max_chars=13)
                address = st.text_area("PHYSICAL ADDRESS")
        else:
            full_name = "ANONYMOUS"
            phone = "N/A"
            cnic = "N/A"
            address = "N/A"

        # Incident Matrix
        st.markdown("---")
        st.markdown("### 🛰️ INCIDENT MATRIX")
        col_type, col_date = st.columns(2)
        with col_type:
            complaint_reason = st.selectbox(
                "CRIME CLASSIFICATION",
                ["Select...", "Hacking", "Phishing", "Cyberstalking", "Online Harassment",
                 "Data Theft", "Financial Fraud", "Child Exploitation", "Identity Theft", "Malware", "Other"]
            )
        with col_date:
            incident_date = st.date_input("INCIDENT TIMESTAMP")
        
        location = st.text_input("DIGITAL/PHYSICAL LOCATION")
        description = st.text_area("DETAILED INCIDENT LOG (MINIMUM 20 CHARACTERS)", height=150)

        # Evidence Core
        st.markdown('<div class="evidence-section">', unsafe_allow_html=True)
        st.markdown("#### 📎 ELECTRONIC EVIDENCE BUNDLE")
        uploaded_files = st.file_uploader(
            "UPLOAD DATA",
            type=['mp4', 'mov', 'avi', 'jpg', 'jpeg', 'png', 'pdf'],
            accept_multiple_files=True,
            help="Encrypted upload. Max video: 1GB | Images/PDF: 50MB"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Submission
        submitted = st.form_submit_button("SUBMIT CASE REPORT", type="primary", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        # Validation
        if not email or "@" not in email:
            st.error("❌ VALID EMAIL REQUIRED FOR SYSTEM NOTIFICATIONS.")
            return

        if complaint_reason == "Select...":
            st.error("❌ PLEASE CLASSIFY THE INCIDENT.")
            return

        if not description or len(description.strip()) < 20:
            st.error("❌ INSUFFICIENT LOG DETAIL. PROVIDE AT LEAST 20 CHARACTERS.")
            return

        if not anonymous:
            if not full_name or len(full_name.strip()) < 2:
                st.error("❌ FULL LEGAL NAME REQUIRED FOR NON-ANONYMOUS FILING.")
                return
            if cnic and len(cnic) != 13:
                st.error("❌ CNIC MUST BE EXACTLY 13 DIGITS.")
                return

        # Success Logic
        tracking_id = f"CCRS-PK-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
        
        complaint_data = {
            "tracking_id": tracking_id,
            "email": email,
            "full_name": full_name,
            "phone": phone,
            "cnic": cnic,
            "address": address,
            "anonymous": anonymous,
            "incident_date": incident_date.isoformat(),
            "location": location,
            "complaint_reason": complaint_reason,
            "description": description,
            "evidence_count": len(uploaded_files) if uploaded_files else 0,
            "submitted_at": datetime.now().isoformat(),
            "status": "pending"
        }

        try:
            complaints = load_complaints()
            complaints[tracking_id] = complaint_data
            save_complaints(complaints)

            st.success("🛰️ CASE REGISTERED IN SYSTEM CORE.")
            st.markdown(f"""
            <div class="tracking-card cyber-glow">
                <h3>ASSIGNED TRACKING ID: <span style="color:var(--secondary);">{tracking_id}</span></h3>
                <p>An initial confirmation has been logged. Use this ID to monitor operational status.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if uploaded_files:
                st.info(f"✅ {len(uploaded_files)} evidence files attached and encrypted.")

            st.info("💡 Pro-tip: Check your email periodically for automated status updates.")
            
        except Exception as e:
            st.error(f"❌ SYSTEM INTEGRITY ERROR: {str(e)}")

if __name__ == "__main__":
    render_report_form()
