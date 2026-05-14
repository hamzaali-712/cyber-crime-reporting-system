"""
Officer Login and Authentication Page
Modern Premium Version
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Officer database file
OFFICERS_FILE = ROOT_DIR / "backend" / "data" / "officers.json"

def load_officers():
    if os.path.exists(OFFICERS_FILE):
        try:
            with open(OFFICERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_officers(officers_data):
    os.makedirs(OFFICERS_FILE.parent, exist_ok=True)
    with open(OFFICERS_FILE, 'w') as f:
        json.dump(officers_data, f, indent=2)

def render_officer_login(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Officer Auth - Cyber System", page_icon="🔐", layout="centered")
    
    st.markdown("""
    <div style="text-align:center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; letter-spacing: 0.1em; color: var(--secondary) !important;">🔐 AUTHENTICATION NODE</h1>
        <p style="color: var(--text-muted);">Restricted Access for Cybercrime Analysts & Law Enforcement</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 3, 1])
    
    with col_m:
        st.markdown('<div class="login-form cyber-glow">', unsafe_allow_html=True)
        st.subheader("OFFICER CREDENTIALS")
        
        officer_id = st.text_input("NODE ID", placeholder="CYBER2026HAMZA")
        password = st.text_input("SECURE KEY", type="password", placeholder="••••••••")
        
        c1, c2 = st.columns(2)
        with c1:
            login_btn = st.button("AUTHORIZE", type="primary", use_container_width=True)
        with c2:
            signup_btn = st.button("REQUEST ID", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if signup_btn:
        st.session_state.show_registration = True
        st.rerun()
    
    if login_btn:
        if not officer_id or not password:
            st.error("❌ ALL CREDENTIALS REQUIRED.")
            return
        
        if verify_officer(officer_id, password):
            st.session_state.officer_logged_in = True
            st.session_state.officer_id = officer_id
            st.success(f"✅ ACCESS GRANTED. WELCOME ANALYST {officer_id}.")
            
            # Navigate after small delay
            import time
            time.sleep(1)
            st.session_state.current_page = "officer_panel"
            st.rerun()
        else:
            st.error("❌ AUTHENTICATION FAILED. INVALID CREDENTIALS.")

    if st.session_state.get("show_registration"):
        show_registration_form()

def verify_officer(officer_id, password):
    officers = load_officers()
    if officer_id in officers:
        return officers[officer_id].get("password") == password
    return False

def show_registration_form():
    st.markdown("---")
    st.markdown("### 📝 OFFICER ENROLLMENT")
    
    col_l, col_m, col_r = st.columns([1, 4, 1])
    
    with col_m:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        name = st.text_input("FULL NAME", placeholder="Enter legal name")
        role = st.selectbox("OPERATIONAL ROLE", ["Inspector", "Analyst", "Cyber Expert", "Superintendent"])
        email = st.text_input("OFFICIAL EMAIL", placeholder="id@police.gov.pk")
        p1 = st.text_input("SET PASSWORD", type="password")
        p2 = st.text_input("CONFIRM PASSWORD", type="password")
        
        if st.button("INITIALIZE REGISTRATION", type="primary", use_container_width=True):
            if not all([name, role, email, p1]):
                st.error("ALL FIELDS REQUIRED.")
                return
            if p1 != p2:
                st.error("PASSWORDS DO NOT MATCH.")
                return
            
            # ID Generation
            generated_id = f"CYBER2026{name.replace(' ', '').upper()}"
            
            officers = load_officers()
            officers[generated_id] = {
                "name": name,
                "designation": role,
                "email": email,
                "password": p1,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            save_officers(officers)
            
            st.success(f"✅ REGISTRATION COMPLETE. YOUR NODE ID IS: {generated_id}")
            st.session_state.show_registration = False
            
        st.markdown('</div>', unsafe_allow_html=True)

def is_officer_logged_in():
    return st.session_state.get("officer_logged_in", False)

def get_current_officer_id():
    return st.session_state.get("officer_id")

def logout_officer():
    st.session_state.officer_logged_in = False
    st.session_state.officer_id = None
