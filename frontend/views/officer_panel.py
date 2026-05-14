"""
Officer Panel - Case Management Dashboard
Includes AI Automation for Victim Communication.
"""

import streamlit as st
import json
import os
import sys
import requests
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

def draft_ai_email(c, decision, officer_notes):
    """Uses AI to draft a detailed, professional email including all case data."""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        prompt = f"""
        Draft a formal official email from NCIA Pakistan to a citizen.
        
        CASE DATA:
        - Name: {c.get('full_name', 'N/A')}
        - CNIC: {c.get('cnic', 'N/A')}
        - Reason: {c.get('complaint_reason')}
        - Description: {c.get('description')}
        - Decision: {decision}
        - Remarks: {officer_notes}
        
        Tone: Formal, Official, Supportive. Use 'NCIA Operations' as the sender.
        """
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": "Legal Secretary."}, {"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except:
        return f"Case Update: {decision}\n\nRemarks: {officer_notes}"
    return "Drafting failed."

def render_officer_panel(set_page_config: bool = True):
    if set_page_config:
        try:
            st.set_page_config(page_title="Officer Dashboard", page_icon="👮", layout="wide")
        except:
            pass
    
    if not st.session_state.get('officer_logged_in'):
        st.error("❌ ACCESS DENIED.")
        return
    
    officer_id = st.session_state.get('officer_id')
    st.markdown(f"### 👮 OFFICER DASHBOARD | `{officer_id}`")
    
    complaints = load_json(COMPLAINTS_FILE)
    decisions = load_json(OFFICER_DECISIONS_FILE)
    
    tab1, tab2, tab3 = st.tabs(["📥 QUEUE", "✅ PROCESSED", "🤖 AI AUTOMATION"])
    
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
                            <p style="font-size: 0.8rem; opacity: 0.7;">ID: {tid} | Citizen: {c.get('full_name', 'Anonymous')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("REVIEW", key=f"rev_{tid}"):
                            st.session_state.review_tid = tid
                            st.rerun()

    # Manual Review Logic - ENHANCED DETAILS
    if st.session_state.get('review_tid'):
        tid = st.session_state.review_tid
        c = complaints[tid]
        st.markdown("---")
        st.subheader(f"🔍 CASE DOSSIER: {tid}")
        
        # Display Complete Details
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 👤 Citizen Information")
            st.write(f"**Full Name:** {c.get('full_name', 'N/A')}")
            st.write(f"**CNIC:** {c.get('cnic', 'N/A')}")
            st.write(f"**Phone:** {c.get('phone', 'N/A')}")
            st.write(f"**Email:** {c.get('email', 'N/A')}")
            st.write(f"**Address:** {c.get('address', 'N/A')}")

        with col2:
            st.markdown("### 🛰️ Incident Details")
            st.write(f"**Crime Type:** {c.get('complaint_reason')}")
            st.write(f"**Date of Incident:** {c.get('incident_date')}")
            st.write(f"**Incident Location:** {c.get('location', 'N/A')}")
            st.write(f"**Evidence Files:** {c.get('evidence_count', 0)}")
            st.write(f"**Submission Date:** {c.get('submitted_at')}")

        st.markdown("### 📄 Incident Description")
        st.info(c.get('description'))
        
        with st.form("action_form"):
            st.markdown("### ⚡ Operational Decision")
            decision = st.selectbox("Assign Status:", ["Approve", "Solve", "Reject"])
            notes = st.text_area("Officer Remarks (Private Log):")
            
            c_sub, c_can = st.columns(2)
            if c_sub.form_submit_button("SUBMIT DECISION", use_container_width=True):
                decisions[tid] = {"officer_id": officer_id, "decision": decision, "notes": notes, "timestamp": datetime.now().isoformat()}
                save_json(OFFICER_DECISIONS_FILE, decisions)
                st.session_state.review_tid = None
                st.success("Decision Logged.")
                st.rerun()
            if c_can.form_submit_button("CLOSE DOSSIER", use_container_width=True):
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
                <p style="font-size: 0.8rem; opacity: 0.7;">ID: {tid} | Note: {d['notes']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("🤖 AI AUTOMATION CENTER")
        processed_tids = list(decisions.keys())
        if not processed_tids:
            st.warning("No processed cases found.")
        else:
            selected_tid = st.selectbox("Select Case to Notify:", processed_tids)
            if selected_tid:
                c = complaints.get(selected_tid)
                d = decisions.get(selected_tid)
                st.markdown("---")
                db_email = c.get('email', '')
                victim_email = st.text_input("Recipient Email:", value=db_email)
                
                if st.button("🪄 GENERATE AI DRAFT"):
                    with st.spinner("Analyzing..."):
                        draft = draft_ai_email(c, d['decision'], d['notes'])
                        st.session_state.ai_draft = draft
                
                if st.session_state.get('ai_draft'):
                    final_draft = st.text_area("Review AI Draft:", value=st.session_state.ai_draft, height=400)
                    if st.button("📧 DISPATCH EMAIL", type="primary"):
                        if not victim_email:
                            st.error("Email required.")
                        else:
                            success, err_msg = send_case_update_email(victim_email, selected_tid, d['decision'], final_draft)
                            if success:
                                st.success("Notification Dispatched.")
                                st.session_state.ai_draft = None
                            else:
                                st.error(f"Dispatch Failed: {err_msg}")

if __name__ == "__main__":
    render_officer_panel()
