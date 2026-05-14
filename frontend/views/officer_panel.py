"""
Officer Panel - Operational Dashboard
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
        try:
            st.set_page_config(page_title="Officer Dashboard", page_icon="👮", layout="wide")
        except:
            pass # Already set by app.py
    
    if not st.session_state.get('officer_logged_in'):
        st.error("❌ ACCESS DENIED.")
        return
    
    officer_id = st.session_state.get('officer_id')
    st.markdown(f"### 👮 OFFICER DASHBOARD | `{officer_id}`")
    
    complaints = load_json(COMPLAINTS_FILE)
    decisions = load_json(OFFICER_DECISIONS_FILE)
    
    tab1, tab2 = st.tabs(["📥 QUEUE", "✅ PROCESSED"])
    
    with tab1:
        pending = [tid for tid in complaints if tid not in decisions]
        if not pending:
            st.info("Queue clear.")
        else:
            for tid in pending:
                c = complaints[tid]
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="complaint-card">
                            <span class="status-pill status-pending">PENDING</span>
                            <h4 style="margin: 5px 0;">{c.get('complaint_reason')}</h4>
                            <p style="font-size: 0.8rem; opacity: 0.7;">ID: {tid}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("REVIEW", key=f"rev_{tid}"):
                            st.session_state.review_tid = tid
                            st.rerun()

    if st.session_state.get('review_tid'):
        tid = st.session_state.review_tid
        c = complaints[tid]
        st.markdown("---")
        st.subheader(f"Case Review: {tid}")
        st.info(c.get('description'))
        
        with st.form("action_form"):
            decision = st.selectbox("Decision:", ["Approve", "Solve", "Reject"])
            notes = st.text_area("Remarks:")
            if st.form_submit_button("SUBMIT DECISION"):
                decisions[tid] = {
                    "officer_id": officer_id,
                    "decision": decision,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                }
                save_json(OFFICER_DECISIONS_FILE, decisions)
                
                # Email
                email = c.get('email')
                if email:
                    send_case_update_email(email, tid, decision, notes)
                
                st.session_state.review_tid = None
                st.success("Decision logged.")
                st.rerun()
            if st.form_submit_button("CLOSE"):
                st.session_state.review_tid = None
                st.rerun()

    with tab2:
        for tid, d in decisions.items():
            c = complaints.get(tid, {})
            cls = f"status-{d['decision'].lower()}"
            st.markdown(f"""
            <div class="complaint-card">
                <span class="status-pill {cls}">{d['decision']}</span>
                <h4 style="margin: 5px 0;">{c.get('complaint_reason', 'N/A')}</h4>
                <p style="font-size: 0.8rem; opacity: 0.7;">ID: {tid}</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_officer_panel()
