"""
Cyber Crime Reporting System - Main Application
Final Stability Fix for Routing & Authentication
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

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cyber Portal PK",
    page_icon="🛡️",
    layout="wide"
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

def navigate_to(page_name: str):
    st.session_state.current_page = page_name
    st.rerun()

# ── Main ──
def main():
    initialize_session()
    load_css()

    # ── Header ──
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ CYBER CRIME PORTAL</h1>
        <p>Government of Pakistan - Law Enforcement</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### 🗺️ NAVIGATION")
        
        pages = {
            "🏠 Home": "home",
            "📋 Report Crime": "report_form",
            "📍 Track Status": "tracking",
            "📚 Legal Guide": "law_guide",
            "❓ Help Center": "help_support"
        }
        
        # If logged in, add Dashboard to the list
        if st.session_state.get('officer_logged_in'):
            pages = {"👮 DASHBOARD": "officer_panel", **pages}
            
        # Determine the radio index based on current page
        page_list = list(pages.values())
        try:
            current_idx = page_list.index(st.session_state.current_page)
        except ValueError:
            current_idx = 0
            
        selected_label = st.radio("Access Node:", list(pages.keys()), index=current_idx)
        selected_page = pages[selected_label]
        
        # Only navigate if the user manually changed the radio
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()

        st.markdown("---")
        if not st.session_state.get('officer_logged_in'):
            if st.button("🔐 OFFICER LOGIN", use_container_width=True):
                navigate_to("officer_login")
        else:
            st.success(f"ID: {st.session_state.get('officer_id')}")
            if st.button("🚪 LOGOUT", use_container_width=True):
                st.session_state.officer_logged_in = False
                navigate_to("home")

    # ── Page Routing ──
    current = st.session_state.current_page

    try:
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
    except Exception as e:
        st.error(f"Routing Error: {str(e)}")
        if st.button("Back to Home"):
            navigate_to("home")

    # ── Chatbot ──
    from components.chatbot import render_chatbot
    with st.expander("🤖 CYBER ASSISTANT (AI)", expanded=False):
        render_chatbot()

    st.markdown(f"""<div class="footer"><p>© {datetime.now().year} NCIA Pakistan</p></div>""", unsafe_allow_html=True)

def show_home_page():
    st.markdown("### 🛰️ PORTAL NODES")
    c1, c2, c3 = st.columns(3)
    c1.metric("NETWORK", "ENCRYPTED")
    c2.metric("COMPLIANCE", "PECA 2016")
    c3.metric("AVAILABILITY", "ONLINE")
    
    st.markdown("---")
    if st.button("INITIATE COMPLAINT SEQUENCE", type="primary", use_container_width=True):
        navigate_to("report_form")

if __name__ == "__main__":
    main()