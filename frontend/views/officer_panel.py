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

def draft_ai_email(case_details, decision, officer_notes):
    """Uses AI to draft a professional email for the victim."""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        prompt = f"""
        Draft a professional and empathetic email from the NCIA Cybercrime Wing to a victim.
        Case Type: {case_details.get('complaint_reason')}
        Decision: {decision}
        Officer Remarks: {officer_notes}
        
        Use a supportive government tone. Address them as 'Dear Citizen' if name is unknown.
        """
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": "Professional secretary."}, {"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
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
        st.subheader(f"Manual Review: {tid}")
        st.write(f"**Details:** {c.get('description')}")
        
        with st.form("action_form"):
            decision = st.selectbox("Decision:", ["Approve", "Solve", "Reject"])
            notes = st.text_area("Internal Remarks:")
            if st.form_submit_button("SUBMIT DECISION"):
                decisions[tid] = {"officer_id": officer_id, "decision": decision, "notes": notes, "timestamp": datetime.now().isoformat()}
                save_json(OFFICER_DECISIONS_FILE, decisions)
                st.session_state.review_tid = None
                st.success("Decision logged. Go to 'AI Automation' to notify the victim.")
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
                
                # Email detection and override logic
                db_email = c.get('email', '')
                st.write(f"**Detected Email:** `{db_email if db_email else 'N/A'}`")
                
                victim_email = st.text_input("Reciprocal Email (Manual Entry/Override):", value=db_email, placeholder="Enter victim email if missing")
                
                if st.button("🪄 GENERATE AI DRAFT"):
                    with st.spinner("AI is drafting response..."):
                        draft = draft_ai_email(c, d['decision'], d['notes'])
                        st.session_state.ai_draft = draft
                
                if st.session_state.get('ai_draft'):
                    final_draft = st.text_area("Review AI Draft:", value=st.session_state.ai_draft, height=300)
                    if st.button("📧 DISPATCH EMAIL TO VICTIM", type="primary"):
                        if not victim_email or "@" not in victim_email:
                            st.error("Please provide a valid recipient email.")
                        else:
                            with st.spinner("Sending..."):
                                if send_case_update_email(victim_email, selected_tid, d['decision'], final_draft):
                                    st.success(f"Notification sent to {victim_email}")
                                    st.session_state.ai_draft = None
                                else:
                                    st.error("Dispatch failed. Check SMTP settings.")

if __name__ == "__main__":
    render_officer_panel()
