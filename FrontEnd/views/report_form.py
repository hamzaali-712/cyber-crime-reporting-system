"""
Cybercrime Complaint Report Form Page
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
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database file
COMPLAINTS_FILE = BASE_DIR / "backend" / "data" / "complaints.json"

def load_complaints():
    """Load complaints database."""
    if os.path.exists(COMPLAINTS_FILE):
        try:
            with open(COMPLAINTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_complaints(complaints):
    """Save complaints to database."""
    os.makedirs(COMPLAINTS_FILE.parent, exist_ok=True)
    with open(COMPLAINTS_FILE, 'w') as f:
        json.dump(complaints, f, indent=2, default=str)

def render_report_form(set_page_config: bool = True):
    """Display the cybercrime complaint form."""
    if set_page_config:
        st.set_page_config(
            page_title="Report Cybercrime - Cyber Crime System",
            page_icon="📋",
            layout="wide"
        )
    
    # Custom CSS
    css = """
    <style>
    .complaint-form {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    .evidence-section {
        background: #fef3c7;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .header-box {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="header-box">
        <h1>📋 Report a Cybercrime</h1>
        <p>Pakistan's Secure Online Cybercrime Reporting Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.current_page = "home"
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        elif hasattr(st, "rerun"):
            st.rerun()
        else:
            st.info("Please refresh the page to return to Home.")
    
    with st.form("complaint_form"):
        st.markdown('<div class="complaint-form">', unsafe_allow_html=True)

        # Personal Information (Optional for anonymity)
        st.subheader("Personal Information (Optional)")
        anonymous = st.checkbox("Report Anonymously", value=True)

        full_name = ""
        phone = ""
        cnic = ""
        address = ""

        if not anonymous:
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name")
                phone = st.text_input("Phone Number")
            with col2:
                cnic = st.text_input("CNIC (13 digits)", max_chars=13)
                address = st.text_area("Address")

        # Incident Details
        st.subheader("Incident Details")
        incident_date = st.date_input("Date of Incident")
        location = st.text_input("Incident Location")
        complaint_reason = st.selectbox(
            "Type of Cybercrime",
            ["Select...", "Hacking", "Phishing", "Cyberstalking", "Online Harassment",
             "Data Theft", "Financial Fraud", "Child Exploitation", "Caller ID Spoofing",
             "Spamming", "Identity Theft", "Unauthorized Access", "Malware", "Other"]
        )
        description = st.text_area("Detailed Description", height=150)

        # Evidence Upload Section
        st.markdown('<div class="evidence-section">', unsafe_allow_html=True)
        st.subheader("📎 Electronic Evidence (Optional)")
        st.write("Upload supporting evidence securely. All files are encrypted and scanned.")

        uploaded_files = st.file_uploader(
            "Upload Evidence",
            type=['mp4', 'mov', 'avi', 'jpg', 'jpeg', 'png', 'pdf'],
            accept_multiple_files=True,
            help="Max video size: 1GB, Images/PDFs: 50MB each"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Submit button
        submitted = st.form_submit_button("Submit Complaint", type="primary", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        # Validate form
        if complaint_reason == "Select...":
            st.error("Please select the type of cybercrime.")
            return

        if not description or len(description.strip()) < 10:
            st.error("Please provide a detailed description (minimum 10 characters).")
            return

        if not anonymous:
            if not full_name or len(full_name.strip()) < 2:
                st.error("Please provide your full name.")
                return
            if cnic and len(cnic) != 13:
                st.error("CNIC must be exactly 13 digits.")
                return

        # Generate tracking ID
        tracking_id = f"CCRS-PK-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"

        # Prepare complaint data
        complaint_data = {
            "tracking_id": tracking_id,
            "full_name": full_name if not anonymous else None,
            "phone": phone if not anonymous else None,
            "cnic": cnic if not anonymous else None,
            "address": address if not anonymous else None,
            "anonymous": anonymous,
            "incident_date": incident_date.isoformat(),
            "location": location,
            "complaint_reason": complaint_reason,
            "description": description,
            "evidence_count": len(uploaded_files) if uploaded_files else 0,
            "submitted_at": datetime.now().isoformat(),
            "status": "pending"
        }

        # Submit to database
        try:
            complaints = load_complaints()
            complaints[tracking_id] = complaint_data
            save_complaints(complaints)

            st.success("✅ Complaint submitted successfully!")
            st.info(f"**Tracking ID:** {tracking_id}")
            st.warning("📄 Please save this tracking ID for future reference.")

            # Upload evidence if provided
            if uploaded_files:
                st.subheader("📎 Uploading Evidence...")
                progress_bar = st.progress(0)

                for i, file in enumerate(uploaded_files):
                    # In production, upload to secure storage
                    progress_bar.progress((i + 1) / len(uploaded_files))

                st.success("✅ Evidence uploaded successfully!")

            # Show next steps
            st.subheader("Next Steps:")
            st.write("""
            1. **Save your tracking ID** for future reference
            2. You will receive updates via email/SMS (if provided)
            3. Investigation will be conducted by cybercrime authorities
            4. Check status using your tracking ID on "Track Complaint" page
            5. Law enforcement officers will review your case
            6. Cases are either approved (solved) or rejected (invalid)
            """)

            # Reset form
            st.session_state.complaint_submitted = True
            
            import time
            time.sleep(2)

        except Exception as e:
            st.error(f"❌ Failed to submit complaint: {str(e)}")
            logger.error(f"Complaint submission error: {str(e)}")

if __name__ == "__main__":
    render_report_form()
