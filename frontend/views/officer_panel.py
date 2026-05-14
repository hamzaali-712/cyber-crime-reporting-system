"""
Officer Panel - Case Management Dashboard
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

from backend.utils.email_service import send_case_update_email

# Database files
COMPLAINTS_FILE = ROOT_DIR / "backend" / "data" / "complaints.json"
OFFICER_DECISIONS_FILE = ROOT_DIR / "backend" / "data" / "officer_decisions.json"

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(file_path, data):
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def render_officer_panel(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Officer Dashboard", page_icon="👮", layout="wide")
    
    if not st.session_state.get('officer_logged_in'):
        st.error("❌ UNAUTHORIZED ACCESS.")
        if st.button("GO TO LOGIN"):
            st.session_state.current_page = "officer_login"
            st.rerun()
        return
    
    officer_id = st.session_state.officer_id
    st.markdown(f"### 👮 COMMAND CENTER | ID: `{officer_id}`")
    
    tab1, tab2, tab3 = st.tabs(["📥 PENDING", "✅ PROCESSED", "📊 ANALYTICS"])
    
    complaints = load_json(COMPLAINTS_FILE)
    decisions = load_json(OFFICER_DECISIONS_FILE)

    with tab1:
        pending = [tid for tid in complaints if tid not in decisions]
        if not pending:
            st.info("No pending cases.")
        else:
            for tid in pending:
                c = complaints[tid]
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="complaint-card">
                            <span class="status-pill status-pending">PENDING</span>
                            <h4 style="margin: 10px 0;">{c.get('complaint_reason')}</h4>
                            <p style="font-size: 0.85rem; opacity: 0.8;">ID: {tid} | Date: {c.get('incident_date')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.write("")
                        if st.button("REVIEW", key=f"rev_{tid}", use_container_width=True):
                            st.session_state.selected_case = tid
                            st.rerun()

    if st.session_state.get('selected_case'):
        tid = st.session_state.selected_case
        c = complaints[tid]
        st.markdown("---")
        st.subheader(f"Case Review: {tid}")
        
        with st.expander("📄 VIEW FULL DETAILS", expanded=True):
            st.write(f"**Type:** {c.get('complaint_reason')}")
            st.write(f"**Description:** {c.get('description')}")
            st.write(f"**Email:** {c.get('email', 'N/A')}")
        
        # Decision Form
        with st.form("decision_form"):
            decision = st.selectbox("Action:", ["Approve", "Solve", "Reject"])
            notes = st.text_area("Officer Remarks:", placeholder="Details for the citizen...")
            
            sub_col, can_col = st.columns(2)
            if sub_col.form_submit_button("SUBMIT & NOTIFY", use_container_width=True):
                # Update records
                decisions[tid] = {
                    "officer_id": officer_id,
                    "decision": decision,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                }
                save_json(OFFICER_DECISIONS_FILE, decisions)
                
                # Email notification
                user_email = c.get('email')
                if user_email:
                    with st.spinner("Dispatching Notification..."):
                        success = send_case_update_email(user_email, tid, decision, notes)
                        if success:
                            st.success("Notification sent.")
                        else:
                            st.error("Email dispatch failed. Check SMTP settings.")
                
                st.session_state.selected_case = None
                st.rerun()
            
            if can_col.form_submit_button("CLOSE", use_container_width=True):
                st.session_state.selected_case = None
                st.rerun()

    with tab2:
        processed = [tid for tid in decisions]
        for tid in processed:
            d = decisions[tid]
            c = complaints.get(tid, {})
            status_cls = f"status-{d['decision'].lower()}"
            st.markdown(f"""
            <div class="complaint-card">
                <span class="status-pill {status_cls}">{d['decision']}</span>
                <h4 style="margin: 10px 0;">{c.get('complaint_reason', 'N/A')}</h4>
                <p style="font-size: 0.85rem; opacity: 0.8;">ID: {tid} | Processed by: {d['officer_id']}</p>
                <p style="font-style: italic; font-size: 0.8rem;">Note: {d['notes']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.metric("TOTAL REPORTS", len(complaints))
        st.metric("RESOLVED", len(processed))
        st.progress(len(processed)/len(complaints) if complaints else 0)

if __name__ == "__main__":
    render_officer_panel()
