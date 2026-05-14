"""
Officer Login - Secure Authentication Node
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OFFICERS_FILE = ROOT_DIR / "backend" / "data" / "officers.json"

def load_officers():
    if os.path.exists(OFFICERS_FILE):
        try:
            with open(OFFICERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def render_officer_login(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Officer Login", page_icon="🔐", layout="centered")

    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    st.markdown("### 🔐 OFFICER AUTHENTICATION")
    
    # Check if already logged in
    if st.session_state.get('officer_logged_in'):
        st.success(f"Authenticated as: {st.session_state.officer_id}")
        if st.button("PROCEED TO DASHBOARD"):
            st.session_state.current_page = "officer_panel"
            st.rerun()
        return

    officer_id = st.text_input("NODE ID (ID)", placeholder="CYBER2026HAMZA")
    password = st.text_input("SECURE KEY (PASSWORD)", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("AUTHORIZE", type="primary", use_container_width=True):
            if verify_officer(officer_id, password):
                st.session_state.officer_logged_in = True
                st.session_state.officer_id = officer_id
                st.session_state.current_page = "officer_panel"
                st.success("ACCESS GRANTED.")
                st.rerun()
            else:
                st.error("CREDENTIALS INVALID.")
    
    with col2:
        if st.button("CANCEL", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

def verify_officer(officer_id, password):
    officers = load_officers()
    if officer_id in officers:
        return officers[officer_id].get("password") == password
    return False

def is_officer_logged_in():
    return st.session_state.get("officer_logged_in", False)

def get_current_officer_id():
    return st.session_state.get("officer_id")

def logout_officer():
    st.session_state.officer_logged_in = False
    st.session_state.officer_id = None
