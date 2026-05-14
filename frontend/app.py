"""
Cyber Crime Reporting System - Main Streamlit Application

A secure platform for reporting cybercrimes with electronic evidence management.
Government-grade security with privacy-by-design principles.

Entry points:
  - Local:  streamlit run frontend/app.py  (from repo root)
  - Cloud:  streamlit_app.py delegates here via runpy
"""

import streamlit as st
import os
import sys
import pathlib
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid

# ── Path setup (must run before any local imports) ────────────────────────────
# Add BOTH the repo root AND the frontend/ directory to sys.path.
# This lets us write:  from views.xxx import yyy   (simple, always works)
# regardless of whether we were launched from repo-root or from inside frontend/
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR     = FRONTEND_DIR.parent

for _p in (str(ROOT_DIR), str(FRONTEND_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Environment & logging ─────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Cyber Crime Reporting System - Pakistan",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
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

# ── Session management ────────────────────────────────────────────────────────
def initialize_session():
    """Initialize secure session state."""
    defaults = {
        'user_authenticated': False,
        'complaint_data': {},
        'evidence_files': [],
        'tracking_id': None,
        'current_page': 'home',
        'officer_logged_in': False,
        'officer_id': None,
        'selected_complaint': None,
        'selected_complaint_data': None,
        'show_registration': False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def rerun_page():
    """Rerun the Streamlit app using the available rerun API."""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def navigate_to(page_name: str):
    """Navigate to a specific page within the app."""
    st.session_state.current_page = page_name
    rerun_page()

# ── Home page ─────────────────────────────────────────────────────────────────
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

# ── Main application ──────────────────────────────────────────────────────────
def main():
    """Main application entry point."""
    try:
        initialize_session()
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
                "home":         0,
                "report_form":  1,
                "tracking":     2,
                "law_guide":    3,
                "help_support": 4,
            }
            page = st.radio(
                "Select Section:",
                page_options,
                index=page_index_map.get(st.session_state.current_page, 0)
            )

            st.markdown("---")
            st.subheader("🔐 Staff Area")
            if st.button("👮 Officer Panel Login"):
                navigate_to("officer_login")

            st.markdown("---")
            st.markdown("**Emergency Contacts:**")
            st.markdown("• Police: 15")
            st.markdown("• FIA Cybercrime: [Contact]")
            st.markdown("• NCCIA: [Contact]")

        # Sync sidebar radio with session state
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

        # ── Page routing ──────────────────────────────────────────────────────
        # All view imports use simple `from views.xxx` because FRONTEND_DIR is on sys.path.
        current = st.session_state.current_page

        if current == "home":
            show_home_page()

        elif current == "report_form":
            from views.report_form import render_report_form
            render_report_form(set_page_config=False)

        elif current == "tracking":
            from views.tracking import render_tracking_page
            render_tracking_page(set_page_config=False)

        elif current == "law_guide":
            from views.law_guide import render_law_guide_page
            render_law_guide_page()

        elif current == "help_support":
            from views.help import render_help_page
            render_help_page()

        elif current == "officer_login":
            from views.officer_login import render_officer_login
            render_officer_login(set_page_config=False)

        elif current == "officer_panel":
            from views.officer_panel import render_officer_panel
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
        import traceback
        st.code(traceback.format_exc(), language="python")


if __name__ == "__main__":
    main()