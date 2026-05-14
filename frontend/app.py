"""
Cyber Crime Reporting System - Main Streamlit Application
High-Performance Version with AI Integration
"""

import streamlit as st
import os
import sys
import pathlib
from dotenv import load_dotenv
import logging
from datetime import datetime

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
    page_title="Cyber Crime Portal - PK",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS Loader ─────────────────────────────────────────────────────────
def load_css():
    css_path = FRONTEND_DIR / "static" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session management ────────────────────────────────────────────────────────
def initialize_session():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'officer_logged_in' not in st.session_state:
        st.session_state.officer_logged_in = False
    if 'officer_id' not in st.session_state:
        st.session_state.officer_id = None

def navigate_to(page_name: str):
    st.session_state.current_page = page_name
    st.rerun()

# ── Main Application Logic ───────────────────────────────────────────────────
def main():
    initialize_session()
    load_css()

    # ── Header ──
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ CYBER CRIME REPORTING</h1>
        <p>Official Law Enforcement Portal - Pakistan</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### 🗺️ NAVIGATION")
        
        # Navigation Map
        pages = {
            "Home": "home",
            "Report Crime": "report_form",
            "Track Status": "tracking",
            "Legal Guide": "law_guide",
            "Help Center": "help_support"
        }
        
        # Determine current index
        current_page = st.session_state.current_page
        page_list = list(pages.values())
        try:
            default_idx = page_list.index(current_page)
        except ValueError:
            default_idx = 0
            
        selected = st.radio("Access Node:", list(pages.keys()), index=default_idx)
        
        if pages[selected] != st.session_state.current_page:
            st.session_state.current_page = pages[selected]
            st.rerun()

        st.markdown("---")
        if not st.session_state.officer_logged_in:
            if st.button("👮 OFFICER LOGIN", use_container_width=True):
                navigate_to("officer_login")
        else:
            st.success(f"Log: {st.session_state.officer_id}")
            if st.button("📊 GO TO PANEL", use_container_width=True):
                navigate_to("officer_panel")
            if st.button("🚪 LOGOUT", use_container_width=True):
                st.session_state.officer_logged_in = False
                st.session_state.officer_id = None
                navigate_to("home")

    # ── Page Routing ──
    current = st.session_state.current_page

    # Import views dynamically to avoid circular issues
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

    # ── Chatbot Overlay ──
    from components.chatbot import render_chatbot
    with st.expander("💬 AI CYBER ASSISTANT", expanded=False):
        render_chatbot()

    # Footer
    st.markdown(f"""
    <div class="footer">
        <p>© {datetime.now().year} National Cybercrime Investigation Agency</p>
    </div>
    """, unsafe_allow_html=True)

def show_home_page():
    st.markdown("### 🛰️ GLOBAL THREAT MONITOR")
    c1, c2, c3 = st.columns(3)
    c1.metric("NETWORK STATUS", "ENCRYPTED", "SECURE")
    c2.metric("LEGAL UPTIME", "100%", "PECA 2016")
    c3.metric("RESPONSE TIME", "< 24H", "ACTIVE")
    
    st.markdown("---")
    st.info("💡 **Welcome to the Portal.** Use the sidebar to report incidents or track your existing cases.")
    
    if st.button("INITIATE REPORTING SEQUENCE", type="primary", use_container_width=True):
        navigate_to("report_form")

if __name__ == "__main__":
    main()