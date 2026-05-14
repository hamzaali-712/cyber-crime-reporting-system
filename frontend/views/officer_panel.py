"""
Officer Panel - Case Management Dashboard
Includes AI Automation and Evidence Review.
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
EVIDENCE_BASE_DIR = ROOT_DIR / "backend" / "data" / "evidence"

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
    """AI drafting for victim updates."""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        prompt = f"Draft official email for case {c.get('tracking_id')}. Type: {c.get('complaint_reason')}. Decision: {decision}. Notes: {officer_notes}."
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        return res.json()["choices"][0]["message"]["content"]
    except:
        return f"Case Update: {decision}\n\nRemarks: {officer_notes}"

def render_officer_panel(set_page_config: bool = True):
    if set_page_config:
        try: st.set_page_config(page_title="Officer Dashboard", layout="wide")
        except: pass
    
    if not st.session_state.get('officer_logged_in'):
        st.error("ACCESS DENIED.")
        return
    
    officer_id = st.session_state.get('officer_id')
    st.markdown(f"### 👮 OFFICER DASHBOARD | `{officer_id}`")
    
    complaints = load_json(COMPLAINTS_FILE)
    decisions = load_json(OFFICER_DECISIONS_FILE)
    
    tab1, tab2, tab3 = st.tabs(["📥 QUEUE", "✅ PROCESSED", "🤖 AI AUTOMATION"])
    
    with tab1:
        pending = [tid for tid in complaints if tid not in decisions]
        for tid in pending:
            c = complaints[tid]
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""<div class="complaint-card"><span class="status-pill status-pending">PENDING</span>
                    <h4 style="margin:5px 0;">{c.get('complaint_reason')}</h4><p>ID: {tid}</p></div>""", unsafe_allow_html=True)
                with col2:
                    if st.button("REVIEW", key=f"rev_{tid}"):
                        st.session_state.review_tid = tid
                        st.rerun()

    # Case Dossier Review
    if st.session_state.get('review_tid'):
        tid = st.session_state.review_tid
        c = complaints[tid]
        st.markdown("---")
        st.subheader(f"🔍 CASE DOSSIER: {tid}")
        
        # Details Columns
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 👤 Citizen Data")
            st.write(f"**Name:** {c.get('full_name')}")
            st.write(f"**CNIC:** {c.get('cnic')}")
            st.write(f"**Address:** {c.get('address')}")
        with c2:
            st.markdown("#### 🛰️ Incident Info")
            st.write(f"**Type:** {c.get('complaint_reason')}")
            st.write(f"**Location:** {c.get('location')}")
            st.write(f"**Date:** {c.get('incident_date')}")

        st.markdown("#### 📄 Description")
        st.info(c.get('description'))

        # ── Evidence Section ──
        st.markdown("#### 📁 EVIDENCE REPOSITORY")
        evidence_files = c.get('evidence_files', [])
        if not evidence_files:
            st.warning("No physical evidence attached to this case.")
        else:
            cols = st.columns(len(evidence_files) if len(evidence_files) < 4 else 4)
            for i, fname in enumerate(evidence_files):
                with cols[i % 4]:
                    fpath = EVIDENCE_BASE_DIR / tid / fname
                    if fpath.exists():
                        with open(fpath, "rb") as f:
                            btn = st.download_button(
                                label=f"📥 {fname[:15]}...",
                                data=f,
                                file_name=fname,
                                key=f"dl_{tid}_{i}"
                            )
                        # Preview images
                        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                            st.image(str(fpath), use_container_width=True)
                    else:
                        st.error("File missing on server.")

        with st.form("action_form"):
            st.markdown("#### ⚡ Operational Decision")
            decision = st.selectbox("Status:", ["Approve", "Solve", "Reject"])
            notes = st.text_area("Officer Remarks:")
            if st.form_submit_button("SUBMIT DECISION", use_container_width=True):
                decisions[tid] = {"officer_id": officer_id, "decision": decision, "notes": notes, "timestamp": datetime.now().isoformat()}
                save_json(OFFICER_DECISIONS_FILE, decisions)
                st.session_state.review_tid = None
                st.success("Decision Logged.")
                st.rerun()
            if st.form_submit_button("CLOSE", use_container_width=True):
                st.session_state.review_tid = None
                st.rerun()

    with tab2:
        for tid, d in decisions.items():
            c = complaints.get(tid, {})
            st.markdown(f'<div class="complaint-card"><h4 style="margin:5px 0;">{c.get("complaint_reason")}</h4><p>ID: {tid}</p></div>', unsafe_allow_html=True)

    with tab3:
        st.subheader("🤖 AI AUTOMATION CENTER")
        # (Same as before but simplified for readability)
        tids = list(decisions.keys())
        if tids:
            sel_tid = st.selectbox("Select Case:", tids)
            if sel_tid:
                c = complaints.get(sel_tid)
                d = decisions.get(sel_tid)
                if st.button("🪄 DRAFT AI UPDATE"):
                    st.session_state.ai_draft = draft_ai_email(c, d['decision'], d['notes'])
                if st.session_state.get('ai_draft'):
                    final = st.text_area("Draft:", value=st.session_state.ai_draft, height=300)
                    if st.button("📧 DISPATCH"):
                        email = c.get('email') or st.text_input("Enter Email:")
                        if email:
                            success, msg = send_case_update_email(email, sel_tid, d['decision'], final)
                            if success: st.success("Sent."); st.session_state.ai_draft = None
                            else: st.error(f"Failed: {msg}")

if __name__ == "__main__":
    render_officer_panel()
