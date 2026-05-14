"""
Officer Login and Authentication Page
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Ensure local frontend imports work properly
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR / "frontend") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "frontend"))

# Officer database file
OFFICERS_FILE = BASE_DIR / "backend" / "data" / "officers.json"

def load_officers():
    """Load officers database."""
    if os.path.exists(OFFICERS_FILE):
        try:
            with open(OFFICERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_officers(officers_data):
    """Save officers database."""
    os.makedirs(OFFICERS_FILE.parent, exist_ok=True)
    with open(OFFICERS_FILE, 'w') as f:
        json.dump(officers_data, f, indent=2)

def render_officer_login(set_page_config: bool = True):
    """Render officer login page."""
    if set_page_config:
        st.set_page_config(
            page_title="Officer Login - Cyber Crime System",
            page_icon="👮",
            layout="centered"
        )
    
    # Custom CSS
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-form {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    .info-box {
        background: #ecfdf5;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
        <h1>👮 Officer Portal</h1>
        <p>Cyber Crime Reporting System - Law Enforcement Access</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.subheader("Officer Login")
        
        officer_id = st.text_input(
            "Officer ID",
            placeholder="CYBER2026HAMZA"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        
        col_login, col_signup = st.columns(2)
        
        with col_login:
            login_btn = st.button("Login", type="primary", use_container_width=True)
        
        with col_signup:
            signup_btn = st.button("Register", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if signup_btn:
        st.session_state.show_registration = True
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        elif hasattr(st, "rerun"):
            st.rerun()
    
    if login_btn:
        if not officer_id or not password:
            st.error("Please enter both Officer ID and password.")
            return
        
        # Mock validation - in production, verify against database
        if verify_officer(officer_id, password):
            st.session_state.officer_logged_in = True
            st.session_state.officer_id = officer_id
            st.success("✅ Login successful!")
            st.info(f"Welcome, {officer_id}!")
            import time
            time.sleep(1)
            st.session_state.current_page = "officer_panel"
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            elif hasattr(st, "rerun"):
                st.rerun()
        else:
            st.error("❌ Invalid Officer ID or password.")
    
    # Information box
    st.markdown("""
    <div class="info-box">
        <h4>Officer ID Format:</h4>
        <p><strong>CYBER2026</strong> + <strong>Your Name</strong></p>
        <p>Example: CYBER2026HAMZA, CYBER2026ALI</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get("show_registration"):
        show_registration_form()

def verify_officer(officer_id, password):
    """Verify officer credentials."""
    officers = load_officers()
    
    if officer_id in officers:
        stored_password = officers[officer_id].get("password")
        return stored_password == password
    
    return False

def show_registration_form():
    """Show officer registration form."""
    st.markdown("---")
    st.subheader("Officer Registration")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        officer_name = st.text_input("Full Name", placeholder="Enter your full name")
        officer_designation = st.selectbox(
            "Designation",
            ["Inspector", "Sub-Inspector", "Constable", "Cyber Expert", "Analyst"]
        )
        officer_email = st.text_input("Official Email", placeholder="name@police.gov.pk")
        officer_phone = st.text_input("Phone Number", placeholder="+92-300-1234567")
        new_password = st.text_input("Set Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Register Officer", type="primary", use_container_width=True):
            if not all([officer_name, officer_designation, officer_email, officer_phone, new_password]):
                st.error("Please fill all fields.")
                return
            
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters long.")
                return
            
            # Generate Officer ID
            officer_id = f"CYBER2026{officer_name.replace(' ', '').upper()}"
            
            # Save to database
            officers = load_officers()
            officers[officer_id] = {
                "name": officer_name,
                "designation": officer_designation,
                "email": officer_email,
                "phone": officer_phone,
                "password": new_password,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            save_officers(officers)
            
            st.success("✅ Registration successful!")
            st.info(f"Your Officer ID: **{officer_id}**")
            st.info("You can now login with your Officer ID and password.")
            
            st.session_state.show_registration = False
        
        st.markdown('</div>', unsafe_allow_html=True)

def is_officer_logged_in():
    """Check if officer is logged in."""
    return st.session_state.get("officer_logged_in", False)

def get_current_officer_id():
    """Get current logged-in officer's ID."""
    return st.session_state.get("officer_id")

def logout_officer():
    """Logout officer."""
    st.session_state.officer_logged_in = False
    st.session_state.officer_id = None
