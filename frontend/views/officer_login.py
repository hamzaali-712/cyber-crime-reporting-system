"""
Officer Login - Secure Authentication Node
Supports Secure Hashed Authentication and Agency Verification Registration.
"""

import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.services.database_service import db_service

# Access passcode defined in environments
SECURITY_ACCESS_PASSCODE = os.getenv("OFFICER_REGISTRATION_PASSCODE", "PAK-CYBER-SECURE-2026")

def render_officer_login(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Officer Authorization Terminal", page_icon="🔐", layout="centered")

    st.markdown('<div class="login-form">', unsafe_allow_html=True)
    st.markdown("### 🔐 OFFICER OPERATIONS TERMINAL")
    
    # Check session
    if st.session_state.get('officer_logged_in'):
        st.success(f"Session Active: {st.session_state.officer_id}")
        if st.button("PROCEED TO INVESTIGATION DASHBOARD", use_container_width=True, type="primary"):
            st.session_state.current_page = "officer_panel"
            st.rerun()
        return

    officer_id = st.text_input("Investigator Node ID", placeholder="E.g., CYBER2026HAMZA")
    password = st.text_input("Operational Secure Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("AUTHORIZE ACCESS", type="primary", use_container_width=True):
            if not officer_id or not password:
                st.error("Please enter both Node ID and Password.")
            else:
                # Direct centralized call which automatically hashes & verifies
                if db_service.verify_officer(officer_id, password):
                    st.session_state.officer_logged_in = True
                    st.session_state.officer_id = officer_id
                    st.session_state.current_page = "officer_panel"
                    st.success("ACCESS GRANTED. Redirecting...")
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: Invalid Node ID or Password.")
    
    with col2:
        if st.button("REGISTER NEW OFFICER", use_container_width=True):
            st.session_state.show_officer_signup = True
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("show_officer_signup"):
        show_registration_form()

def show_registration_form():
    st.markdown("---")
    st.markdown("### 📝 SECURE OFFICER REGISTRATION")
    st.info("Registration requires a validated Agency Security Code. Unauthorized registrations are logged.")
    
    with st.form("officer_signup_form"):
        name = st.text_input("Full Name", placeholder="E.g., Hamza Ali")
        email = st.text_input("Official Government Email", placeholder="E.g., hamza@ncia.gov.pk")
        role = st.selectbox("Operational Assigned Role", ["Inspector", "Analyst", "Cyber Security Specialist"])
        
        # High security passcode verification
        agency_code = st.text_input("Agency Security Code (Required)", type="password", placeholder="Enter the official agency access passcode")
        
        p1 = st.text_input("Set Login Password", type="password", help="Password must be at least 8 characters.")
        p2 = st.text_input("Confirm Login Password", type="password")
        
        col_reg, col_close = st.columns(2)
        
        if col_reg.form_submit_button("CREATE AGENT NODE", use_container_width=True):
            if not all([name, email, agency_code, p1, p2]):
                st.error("Validation Failure: All form fields are required.")
            elif agency_code.strip() != SECURITY_ACCESS_PASSCODE:
                st.error("Authentication Failure: Invalid Agency Security Code. Registration denied.")
                # System audit log for unauthorized attempt
                db_service.create_audit_log(
                    user_id="anonymous",
                    action="UNAUTHORIZED_OFFICER_REGISTRATION_ATTEMPT",
                    resource_type="officer",
                    resource_id=email,
                    details={"name": name, "email": email, "attempted_passcode": agency_code}
                )
            elif len(p1) < 8:
                st.error("Validation Failure: Password must be at least 8 characters long.")
            elif p1 != p2:
                st.error("Validation Failure: Passwords do not match.")
            else:
                # Save via central db_service which automatically secures the record
                officer_data = {
                    "name": name.strip(),
                    "email": email.strip(),
                    "role": role,
                    "password": p1
                }
                
                try:
                    generated_id = db_service.create_officer(officer_data)
                    st.success(f"🔒 ACCOUNT CREATED SUCCESSFULLY!\nYour official Investigator Node ID is: {generated_id}")
                    st.session_state.show_officer_signup = False
                except Exception as e:
                    st.error(f"System Error: Failed to register account: {e}")
        
        if col_close.form_submit_button("CLOSE REGISTRATION", use_container_width=True):
            st.session_state.show_officer_signup = False
            st.rerun()

def logout_officer():
    st.session_state.officer_logged_in = False
    st.session_state.officer_id = None
