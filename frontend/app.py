"""
Cyber Crime Reporting System - Main Streamlit Application
Modern Premium Version
"""

import streamlit as st
import os
import sys
import pathlib
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid

# ── Path setup ────────────────────────────────────────────────────────────────
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR     = FRONTEND_DIR.parent

for _p in (str(ROOT_DIR), str(FRONTEND_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Environment & logging ─────────────────────────────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cyber Crime Reporting System - Pakistan",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS Loader ─────────────────────────────────────────────────────────
def load_css():
    """Load the premium cyber-themed CSS."""
    css_path = FRONTEND_DIR / "static" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback basic styles if file is missing
        st.markdown("""
        <style>
        .main-header { background: #1e3a8a; color: white; padding: 2rem; border-radius: 10px; text-align: center; }
        </style>
        """, unsafe_allow_html=True)

# ── Session management ────────────────────────────────────────────────────────
def initialize_session():
    """Initialize secure session state."""
    defaults = {
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

def navigate_to(page_name: str):
    """Navigate to a specific page."""
    st.session_state.current_page = page_name
    st.rerun()

# ── Application Main ──────────────────────────────────────────────────────────
def main():
    initialize_session()
    load_css()

    # ── Header ──
    st.markdown("""
    <div class="main-header cyber-glow">
        <h1>🛡️ CYBER CRIME PORTAL</h1>
        <p>Pakistan's Advanced Electronic Evidence & Crime Reporting Platform</p>
        <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.7;">
            Securely Compliant with PECA 2016 Standards
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### 🌐 NETWORK NAVIGATION")
        page_options = ["Home", "Report Cybercrime", "Track Complaint", "Cyber Law Guide", "Help & Support"]
        page_index_map = {"home": 0, "report_form": 1, "tracking": 2, "law_guide": 3, "help_support": 4}
        
        selected_page = st.radio(
            "Select Operational Node:",
            page_options,
            index=page_index_map.get(st.session_state.current_page, 0)
        )

        st.markdown("---")
        st.markdown("### 🔐 RESTRICTED ACCESS")
        if st.button("👮 OFFICER LOGIN", use_container_width=True):
            navigate_to("officer_login")

        st.markdown("---")
        st.markdown("### 🚨 EMERGENCY")
        st.error("Police: 15")
        st.info("FIA: helpdesk@nr3c.gov.pk")

    # ── Logic to sync sidebar with session state ──
    reverse_map = {v: k for k, v in page_index_map.items()}
    if selected_page:
        mapped_key = page_options.index(selected_page)
        page_key = reverse_map.get(mapped_key)
        if page_key and st.session_state.current_page != page_key:
            st.session_state.current_page = page_key
            st.rerun()

    # ── Page Routing ──
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

    # ── Footer ──
    st.markdown(f"""
    <div class="footer">
        <h3>🛡️ CYBER SECURE PK</h3>
        <p>National Electronic Crime Management System</p>
        <p style="font-size: 0.8rem; margin-top: 1rem;">
            &copy; {datetime.now().year} - All Rights Reserved | Government of Pakistan
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_home_page():
    st.markdown("## 🛰️ SYSTEM OVERVIEW")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stMetric cyber-glow">
            <h3>🔒 END-TO-END SECURITY</h3>
            <p>Advanced encryption protocols for all reported data and evidence.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="stMetric cyber-glow">
            <h3>⚡ REAL-TIME TRACKING</h3>
            <p>Monitor your case progress with high-precision tracking nodes.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="stMetric cyber-glow">
            <h3>⚖️ LEGAL INTELLIGENCE</h3>
            <p>Guided legal analysis based on Pakistan's PECA 2016 lawbook.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Hero Call to Action
    st.markdown("### 🛡️ DO YOU NEED TO REPORT A CRIME?")
    if st.button("INITIALIZE COMPLAINT FORM", type="primary", use_container_width=True):
        navigate_to("report_form")

if __name__ == "__main__":
    main()