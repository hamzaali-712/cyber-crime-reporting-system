"""
Cyber Crime Reporting System - Officer Portal
Dedicated Secure Administrative Command Center (100% Secure Isolation)
"""

import streamlit as st
import os
import sys
import pathlib
from dotenv import load_dotenv
from datetime import datetime

# ── Path Setup ────────────────────────────────────────────────────────────────
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR     = FRONTEND_DIR.parent

for _p in (str(ROOT_DIR), str(FRONTEND_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

load_dotenv()

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NCIA Officer Command Center",
    page_icon="👮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS Loader ─────────────────────────────────────────────────────────
def load_css():
    css_path = FRONTEND_DIR / "static" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session Management ────────────────────────────────────────────────────────
def initialize_session():
    if 'officer_logged_in' not in st.session_state:
        st.session_state.officer_logged_in = False
    if 'officer_id' not in st.session_state:
        st.session_state.officer_id = None
    if 'current_officer_page' not in st.session_state:
        st.session_state.current_officer_page = 'login'

def navigate_officer_to(page_name: str):
    st.session_state.current_officer_page = page_name
    st.rerun()

# ── Main ──
def main():
    initialize_session()
    load_css()

    # Premium Dashboard Header
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #0b1329 0%, #1c2d5a 100%); border-bottom: 2px solid #3b82f6;">
        <h1>👮 NCIA OFFICER OPERATIONS CENTER</h1>
        <p>Federal Cyber Crime Division - Government of Pakistan | Classified Access Node</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### 🔒 OPERATION STATUS")
        
        if st.session_state.officer_logged_in:
            st.success(f"AUTHENTICATED ID:\n`{st.session_state.officer_id}`")
            
            # Sidebar controls
            if st.button("📊 COMMAND DASHBOARD", use_container_width=True, type="primary"):
                st.session_state.current_officer_page = "dashboard"
                st.rerun()
                
            if st.button("🚪 TERMINATE SESSION (LOGOUT)", use_container_width=True):
                # Centralized Database Service for logging
                from backend.services.database_service import db_service
                db_service.create_audit_log(
                    user_id=st.session_state.officer_id,
                    action="OFFICER_LOGOUT",
                    resource_type="officer",
                    resource_id=st.session_state.officer_id
                )
                
                st.session_state.officer_logged_in = False
                st.session_state.officer_id = None
                st.session_state.current_officer_page = "login"
                if 'review_tid' in st.session_state:
                    st.session_state.review_tid = None
                st.rerun()
        else:
            st.warning("SESSION: NOT AUTHORIZED")
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #f87171; text-align: center;">
                <strong>⚠️ SECURITY WARNING</strong><br>
                This terminal is classified. Unauthorized access attempts are monitored under PECA Section 13-14.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; font-size: 0.75rem; color: #94a3b8;">
            <p>NCIA Operational Hub v2.1<br>Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Page Routing ──
    if not st.session_state.officer_logged_in:
        from views.officer_login import render_officer_login
        render_officer_login(set_page_config=False)
    else:
        from views.officer_panel import render_officer_panel
        render_officer_panel(set_page_config=False)

    st.markdown(f"""<div class="footer"><p>© {datetime.now().year} NCIA Intelligence Branch | Restricted Law Enforcement Access</p></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
