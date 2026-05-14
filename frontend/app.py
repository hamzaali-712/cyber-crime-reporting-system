"""
Cyber Crime Reporting System - Main Streamlit Application

A secure platform for reporting cybercrimes with electronic evidence management.
Government-grade security with privacy-by-design principles.
"""

import streamlit as st
import os
import sys
import pathlib
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid

# Ensure project root is in sys.path for absolute imports
ROOT_DIR = pathlib.Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'


def rerun_page():
    """Rerun the Streamlit app using the available rerun API."""
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        raise RuntimeError("Streamlit rerun is unavailable. Please upgrade Streamlit.")


def navigate_to(page_name: str):
    """Navigate to a specific page within the app."""
    st.session_state.current_page = page_name
    rerun_page()

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
            page_options = ["Home", "Report Cybercrime", "Track Complaint", "Cyber Law Guide", "Help & Support"]
            page_index_map = {
                "home": 0,
                "report_form": 1,
                "tracking": 2,
                "law_guide": 3,
                "help_support": 4,
            }
            page = st.radio(
                "Select Section:",
                page_options,
                index=page_index_map.get(st.session_state.current_page, 0)
            )

            st.markdown("---")
            
            # Officer Panel Access
            st.subheader("🔐 Staff Area")
            if st.button("👮 Officer Panel Login"):
                navigate_to("officer_login")
            
            st.markdown("---")
            st.markdown("**Emergency Contacts:**")
            st.markdown("• Police: 15")
            st.markdown("• FIA Cybercrime: [Contact]")
            st.markdown("• NCCIA: [Contact]")

        # Page routing
        current_page_label = page_options[page_index_map.get(st.session_state.current_page, 0)]
        if page != current_page_label:
            if page == "Home":
                navigate_to("home")
            elif page == "Report Cybercrime":
                navigate_to("report_form")
            elif page == "Track Complaint":
                navigate_to("tracking")
            elif page == "Cyber Law Guide":
                navigate_to("law_guide")
            elif page == "Help & Support":
                navigate_to("help_support")

        if st.session_state.current_page == "home":
            show_home_page()
        elif st.session_state.current_page == "report_form":
            from frontend.views.report_form import render_report_form
            render_report_form(set_page_config=False)
        elif st.session_state.current_page == "tracking":
            from frontend.views.tracking import render_tracking_page
            render_tracking_page(set_page_config=False)
        elif st.session_state.current_page == "law_guide":
            from frontend.views.law_guide import render_law_guide_page
            render_law_guide_page()
        elif st.session_state.current_page == "help_support":
            from frontend.views.help import render_help_page
            render_help_page()
        elif st.session_state.current_page == "officer_login":
            from frontend.views.officer_login import render_officer_login
            render_officer_login(set_page_config=False)
        elif st.session_state.current_page == "officer_panel":
            from frontend.views.officer_panel import render_officer_panel
            render_officer_panel(set_page_config=False)

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
        navigate_to("report_form")

if __name__ == "__main__":
    main()