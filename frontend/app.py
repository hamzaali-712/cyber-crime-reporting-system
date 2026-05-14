"""
Cyber Crime Reporting System - Main Streamlit Application

A secure platform for reporting cybercrimes with electronic evidence management.
Government-grade security with privacy-by-design principles.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid

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

# Page configuration
st.set_page_config(
    page_title="Cyber Crime Reporting System - Pakistan",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for government-style appearance
def load_css():
    """Load custom CSS for professional government-style UI."""
    css = """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
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
    .law-section {
        background: #ecfdf5;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
    }
    .stButton>button {
        background: #1e40af;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 5px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: #1e3a8a;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Security headers and session management
def initialize_session():
    """Initialize secure session state."""
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'complaint_data' not in st.session_state:
        st.session_state.complaint_data = {}
    if 'evidence_files' not in st.session_state:
        st.session_state.evidence_files = []
    if 'tracking_id' not in st.session_state:
        st.session_state.tracking_id = None

# Main application
def main():
    """Main application entry point."""
    try:
        # Initialize session
        initialize_session()

        # Load CSS
        load_css()

        # Main header
        st.markdown("""
        <div class="main-header">
            <h1>🛡️ Cyber Crime Reporting System</h1>
            <p>Pakistan's Secure Online Cybercrime Reporting Platform</p>
            <p style="font-size: 0.9em;">Prevention of Electronic Crimes Act (PECA) 2016 Compliant</p>
        </div>
        """, unsafe_allow_html=True)

        # Sidebar navigation
        with st.sidebar:
            st.title("Navigation")
            page = st.radio(
                "Select Section:",
                ["Home", "Report Cybercrime", "Track Complaint", "Cyber Law Guide", "Help & Support"],
                index=0
            )

            st.markdown("---")
            
            # Officer Panel Access
            st.subheader("🔐 Staff Area")
            if st.button("👮 Officer Panel Login"):
                st.switch_page("pages/officer_login.py")
            
            st.markdown("---")
            st.markdown("**Emergency Contacts:**")
            st.markdown("• Police: 15")
            st.markdown("• FIA Cybercrime: [Contact]")
            st.markdown("• NCCIA: [Contact]")

        # Page routing
        if page == "Home":
            show_home_page()
        elif page == "Report Cybercrime":
            st.switch_page("pages/report_form.py")
        elif page == "Track Complaint":
            from pages.tracking import render_tracking_page
            render_tracking_page()
        elif page == "Cyber Law Guide":
            from pages.law_guide import render_law_guide_page
            render_law_guide_page()
        elif page == "Help & Support":
            from pages.help import render_help_page
            render_help_page()

        # Footer
        st.markdown("""
        <div class="footer">
            <p><strong>Cyber Crime Reporting System</strong> | Developed for Pakistan's Digital Security</p>
            <p>© 2026 - All rights reserved | Privacy Policy | Terms of Service</p>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")
        st.error(f"Error details: {str(e)}")

def show_home_page():
    """Display the home page with system overview."""
    st.header("Welcome to Pakistan's Cyber Crime Reporting System")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔒 Secure Reporting")
        st.write("""
        Report cybercrimes anonymously or with registration.
        Your data is protected with government-grade security.
        """)

        st.subheader("📋 Electronic Evidence")
        st.write("""
        Upload videos, images, and documents securely.
        All evidence is encrypted and malware-scanned.
        """)

    with col2:
        st.subheader("⚖️ Legal Guidance")
        st.write("""
        Access Pakistan's cybercrime laws and regulations.
        Get AI-powered guidance on applicable sections.
        """)

        st.subheader("📄 Official Reports")
        st.write("""
        Generate PDF reports with tracking IDs.
        Government-style formatting with watermarks.
        """)

    st.markdown("---")
    st.subheader("🚨 Report a Cybercrime Now")
    if st.button("Start Complaint Form", type="primary", use_container_width=True):
        st.switch_page("pages/report_form.py")

def show_complaint_form():
    """Display the cybercrime complaint form."""
    st.header("Report a Cybercrime")

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
            ["Hacking", "Phishing", "Cyberstalking", "Online Harassment",
             "Data Theft", "Financial Fraud", "Child Exploitation", "Other"]
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
        submitted = st.form_submit_button("Submit Complaint", type="primary")

        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        # Validate form
        if not complaint_reason:
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

        # Prepare complaint data
        complaint_data = {
            "full_name": full_name if not anonymous else None,
            "phone": phone if not anonymous else None,
            "cnic": cnic if not anonymous else None,
            "address": address if not anonymous else None,
            "incident_date": incident_date.isoformat(),
            "location": location,
            "complaint_reason": complaint_reason,
            "description": description
        }

        # Submit to backend
        try:
            # TODO: Replace with actual API call
            # import requests
            # response = requests.post("http://localhost:8000/complaints/", json=complaint_data)
            # if response.status_code == 200:
            #     result = response.json()
            #     tracking_id = result.get("tracking_id")

            # Mock successful submission for now
            import time
            time.sleep(1)  # Simulate API call
            tracking_id = f"CCRS-PK-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"

            st.success("✅ Complaint submitted successfully!")
            st.info(f"**Tracking ID:** {tracking_id}")
            st.warning("📄 Please save this tracking ID for future reference.")

            # Upload evidence if provided
            if uploaded_files:
                st.subheader("📎 Uploading Evidence...")
                progress_bar = st.progress(0)

                for i, file in enumerate(uploaded_files):
                    # TODO: Implement actual file upload
                    # files_data = {"files": (file.name, file.getvalue(), file.type)}
                    # upload_response = requests.post(
                    #     f"http://localhost:8000/evidence/upload",
                    #     files=files_data,
                    #     data={"complaint_id": tracking_id}
                    # )

                    time.sleep(0.5)  # Simulate upload
                    progress_bar.progress((i + 1) / len(uploaded_files))

                st.success("Evidence uploaded successfully!")

            # Show next steps
            st.subheader("Next Steps:")
            st.write("""
            1. **Save your tracking ID** for future reference
            2. You will receive updates via email/SMS (if provided)
            3. Investigation will be conducted by cybercrime authorities
            4. Check status using your tracking ID
            """)

            # Reset form
            st.session_state.complaint_submitted = True

        except Exception as e:
            st.error(f"❌ Failed to submit complaint: {str(e)}")
            logger.error(f"Complaint submission error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

def show_law_guide():
    """Display the cyber law guide."""
    st.header("Pakistan Cyber Crime Rule Book")

    st.markdown('<div class="law-section">', unsafe_allow_html=True)

    # Import cyber laws data
    import sys
    sys.path.append('data')
    try:
        from cyber_laws import get_all_laws, get_categories, search_laws, get_laws_by_category
        laws_data = get_all_laws()
        categories = get_categories()
    except ImportError:
        st.error("Cyber laws database not loaded. Please ensure cyber_laws.py exists.")
        return

    # Search and filter
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("Search laws...", placeholder="Enter keywords...")
    with col2:
        category_filter = st.selectbox(
            "Filter by category:",
            ["All"] + categories
        )

    # Filter laws
    filtered_laws = laws_data
    if search_term:
        filtered_laws = search_laws(search_term)
    if category_filter != "All":
        filtered_laws = get_laws_by_category(category_filter)

    # Display laws
    if filtered_laws:
        st.subheader(f"📚 Found {len(filtered_laws)} Law(s)")
        
        for law in filtered_laws:
            with st.expander(f"⚖️ Section {law['section']}: {law['title']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Category:** `{law['category']}`")
                    st.markdown(f"**Section:** PECA {law['section']}")
                
                with col2:
                    st.markdown(f"**Applicable To:**")
                    for item in law['applicable_to']:
                        st.markdown(f"• {item}")
                
                st.markdown("---")
                st.markdown("**Description:**")
                st.write(law['description'])
                
                st.markdown("**Details:**")
                st.write(law['details'])
                
                st.warning(f"**Punishment:** {law['punishment']}")
                
                st.markdown(f"*Reference: {law['peca_reference']}*")
    else:
        st.info("❌ No laws found matching your search criteria.")

    st.markdown('</div>', unsafe_allow_html=True)

def show_help_support():
    """Display help and support information."""
    st.header("Help & Support")

    st.subheader("Emergency Contacts")
    st.write("""
    - **Pakistan Police**: Dial 15
    - **FIA Cybercrime Wing**: [Contact Information]
    - **National Cybercrime Investigation Agency (NCIA)**: [Contact Information]
    """)

    st.subheader("Victim Support")
    st.write("""
    If you're a victim of cybercrime:
    1. Preserve all evidence
    2. Don't delete any communications
    3. Report immediately
    4. Seek professional help if needed
    """)

    st.subheader("Frequently Asked Questions")

    faq_data = [
        {
            "question": "What types of cybercrimes can I report?",
            "answer": "You can report hacking, phishing, cyberstalking, online harassment, data theft, financial fraud, child exploitation, and other cybercrimes."
        },
        {
            "question": "Is my report anonymous?",
            "answer": "Yes, you can choose to report anonymously. However, providing contact information helps authorities investigate more effectively."
        },
        {
            "question": "What evidence should I preserve?",
            "answer": "Save emails, messages, screenshots, URLs, transaction records, and any other relevant digital evidence. Do not delete or modify anything."
        },
        {
            "question": "How long does investigation take?",
            "answer": "Investigation time varies depending on the complexity of the case. You will receive updates via your tracking ID."
        },
        {
            "question": "Can I withdraw my complaint?",
            "answer": "Contact the investigating authority using your tracking ID if you need to withdraw or modify your complaint."
        },
        {
            "question": "What if I'm not in Pakistan?",
            "answer": "This system is designed for Pakistani citizens. For international incidents, contact local law enforcement or INTERPOL."
        }
    ]

    for faq in faq_data:
        with st.expander(faq["question"]):
            st.write(faq["answer"])

if __name__ == "__main__":
    main()