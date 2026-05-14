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
        
        # Detailed prompt including all case info
        prompt = f"""
        Draft a comprehensive, professional official email from NCIA Pakistan to a citizen.
        
        CITIZEN DETAILS:
        - Name: {c.get('full_name', 'N/A')}
        - CNIC: {c.get('cnic', 'N/A')}
        - Email: {c.get('email', 'N/A')}
        
        CASE DETAILS:
        - Tracking ID: {c.get('tracking_id')}
        - Category/Reason: {c.get('complaint_reason')}
        - Incident Date: {c.get('incident_date')}
        - Original Description: {c.get('description')}
        
        OPERATIONAL DECISION:
        - Status: {decision}
        - Officer Remarks: {officer_notes}
        
        REQUIREMENTS:
        1. Mention the Category/Reason clearly.
        2. Mention the CNIC and Full Name to verify the recipient.
        3. Acknowledge the original incident description briefly.
        4. Explain the decision ({decision}) and the officer's remarks.
        5. Use a formal, supportive, and authoritative government tone.
        6. Do not use placeholders like [Your Name], write as 'NCIA Operations Unit'.
        """
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": "You are a senior NCIA legal officer."}, {"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1200
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"System Error: {str(e)}\n\nCase Update: {decision}\nRemarks: {officer_notes}"
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

    if st.session_state.get('review_tid'):
        tid = st.session_state.review_tid
        c = complaints[tid]
        st.markdown("---")
        st.subheader(f"Manual Review: {tid}")
        
        with st.form("action_form"):
            decision = st.selectbox("Decision:", ["Approve", "Solve", "Reject"])
            notes = st.text_area("Internal Remarks (Summarize for AI):")
            if st.form_submit_button("SUBMIT DECISION"):
                decisions[tid] = {"officer_id": officer_id, "decision": decision, "notes": notes, "timestamp": datetime.now().isoformat()}
                save_json(OFFICER_DECISIONS_FILE, decisions)
                st.session_state.review_tid = None
                st.success("Decision logged.")
                st.rerun()

    with tab2:
        for tid, d in decisions.items():
            c = complaints.get(tid, {})
            cls = f"status-{d['decision'].lower()}"
            st.markdown(f"""
            <div class="complaint-card">
                <span class="status-pill {cls}">{d['decision']}</span>
                <h4 style="margin: 5px 0;">{c.get('complaint_reason', 'N/A')}</h4>
                <p style="font-size: 0.8rem; opacity: 0.7;">ID: {tid} | Citizen: {c.get('full_name', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("🤖 AI AUTOMATED COMMUNICATION")
        
        processed_tids = list(decisions.keys())
        if not processed_tids:
            st.warning("No processed cases found to automate.")
        else:
            selected_tid = st.selectbox("Select Case to Notify:", processed_tids)
            if selected_tid:
                c = complaints.get(selected_tid)
                d = decisions.get(selected_tid)
                
                st.markdown("---")
                db_email = c.get('email', '')
                victim_email = st.text_input("Reciprocal Email:", value=db_email, placeholder="Enter email")
                
                if st.button("🪄 GENERATE ENHANCED AI DRAFT"):
                    with st.spinner("AI is synthesizing case data..."):
                        draft = draft_ai_email(c, d['decision'], d['notes'])
                        st.session_state.ai_draft = draft
                
                if st.session_state.get('ai_draft'):
                    final_draft = st.text_area("Review Enhanced AI Draft:", value=st.session_state.ai_draft, height=400)
                    if st.button("📧 DISPATCH EMAIL TO VICTIM", type="primary"):
                        if not victim_email:
                            st.error("No recipient email provided.")
                        else:
                            with st.spinner("Initializing secure SMTP dispatch..."):
                                success, err_msg = send_case_update_email(victim_email, selected_tid, d['decision'], final_draft)
                                if success:
                                    st.success(f"Notification successfully dispatched to {victim_email}")
                                    st.session_state.ai_draft = None
                                else:
                                    st.error(f"Dispatch Failed: {err_msg}")

if __name__ == "__main__":
    render_officer_panel()
