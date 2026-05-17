"""
Officer Panel - Case Management Dashboard
Includes AI Automation, Evidence Review, and Audit Trails.
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
from backend.services.database_service import db_service

# Database files
EVIDENCE_BASE_DIR = ROOT_DIR / "backend" / "data" / "evidence"

def get_actual_evidence_files(tracking_id):
    case_dir = EVIDENCE_BASE_DIR / tracking_id
    if case_dir.exists() and case_dir.is_dir():
        return [f for f in os.listdir(case_dir) if os.path.isfile(case_dir / f)]
    return []

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
        
        Include the Tracking ID: {c.get('tracking_id')}
        Tone: Formal, Official, Supportive. Use 'NCIA Operations' as the sender.
        """
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": "Professional secretary."}, {"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Case Update: {decision}\n\nRemarks: {officer_notes}"
    return "Drafting failed."

def render_officer_panel(set_page_config: bool = True):
    if set_page_config:
        try: st.set_page_config(page_title="Officer Dashboard", layout="wide")
        except: pass
    
    if not st.session_state.get('officer_logged_in'):
        st.error("ACCESS DENIED: Session not authorized.")
        return
    
    officer_id = st.session_state.get('officer_id')
    st.markdown(f"### 👮 OFFICER COMMAND DASHBOARD | Active Session: `{officer_id}`")
    
    # Centralized Service Database Reads
    complaints = db_service.get_all_complaints()
    decisions = db_service.get_all_decisions()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📥 PENDING QUEUE", "✅ PROCESSED CASES", "📋 SYSTEM AUDIT LOGS", "🤖 AI AUTOMATION"])
    
    # ── TAB 1: PENDING QUEUE ──
    with tab1:
        # Filter for cases that are pending (status == "pending" or not decided)
        pending = [tid for tid, c in complaints.items() if c.get("status", "pending").lower() == "pending"]
        
        if not pending:
            st.info("Queue is clear! There are no pending complaints to review.")
        else:
            for tid in pending:
                c = complaints[tid]
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="complaint-card" style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <span class="status-pill status-pending">PENDING REVIEW</span>
                                <code style="background: #0f172a; color: #3b82f6; padding: 4px 8px; border-radius: 4px; border: 1px solid #1e40af; font-family: monospace;">{tid}</code>
                            </div>
                            <h4 style="margin: 0; color: #f8fafc;">{c.get('complaint_reason')}</h4>
                            <p style="margin: 5px 0 0 0; font-size: 0.85rem; color: #94a3b8;">Complainant: {c.get('full_name')} | Submitted: {c.get('submitted_at', 'N/A')[:16]}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.write("") # padding
                        if st.button("REVIEW DOSSIER", key=f"rev_{tid}", use_container_width=True):
                            st.session_state.review_tid = tid
                            st.rerun()

    # Manual Review Sub-Section
    if st.session_state.get('review_tid'):
        tid = st.session_state.review_tid
        c = complaints.get(tid)
        
        if not c:
            st.error("Dossier not found.")
            st.session_state.review_tid = None
            st.rerun()
            
        st.markdown("<br><hr style='border: 1px solid #3b82f6;'><br>", unsafe_allow_html=True)
        st.subheader(f"🔍 CASE DOSSIER REVIEW: {tid}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 👤 Complainant Identification Details")
            st.write(f"**Anonymous Submission:** {'Yes' if c.get('anonymous') else 'No'}")
            st.write(f"**Full Name:** {c.get('full_name')}")
            st.write(f"**CNIC Number:** {c.get('cnic')}")
            st.write(f"**Phone Number:** {c.get('phone')}")
            st.write(f"**Email:** {c.get('email')}")
            st.write(f"**Residential Address:** {c.get('address')}")
        with col2:
            st.markdown("#### 🛰️ Incident Specifics")
            st.write(f"**Category:** {c.get('complaint_reason')}")
            st.write(f"**Location Source:** {c.get('location')}")
            st.write(f"**Date of Occurrence:** {c.get('incident_date')}")
            st.write(f"**Record Log Date:** {c.get('submitted_at')[:19]}")

        st.markdown("#### 📄 Case Statement / Description")
        st.info(c.get('description'))

        st.markdown("#### 📁 EVIDENCE REPOSITORY")
        files = get_actual_evidence_files(tid)
        if not files:
            st.warning("No physical evidence files attached to this case.")
        else:
            cols = st.columns(4)
            for i, fname in enumerate(files):
                with cols[i % 4]:
                    fpath = EVIDENCE_BASE_DIR / tid / fname
                    try:
                        with open(fpath, "rb") as f:
                            st.download_button(f"📥 Download: {fname[:15]}...", f, fname, key=f"dl_{tid}_{i}", use_container_width=True)
                        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                            st.image(str(fpath), use_column_width=True)
                    except Exception as e:
                        st.error(f"Error loading evidence: {e}")

        # Review Actions Form
        with st.form("action_form"):
            st.markdown("#### ⚖️ INVESTIGATOR DECISION & REMARKS")
            decision = st.selectbox("Assign Case Action Status:", ["Approve", "Solve", "Reject"], help="Approve puts the case under active investigation. Solve marks it completed. Reject closes the case.")
            notes = st.text_area("Official Case Action Notes / Remarks:", placeholder="Provide details regarding active assignment, evidence validation, or resolution reasons.")
            
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.form_submit_button("SUBMIT DECISION & LOCK", use_container_width=True):
                if not notes.strip():
                    st.error("Remarks and action notes are required to submit an investigator decision.")
                else:
                    # Centralized synced DB update
                    # This updates both files and creates the audit log in a single operation
                    success = db_service.update_complaint_status(
                        tracking_id=tid,
                        status=decision,
                        notes=notes.strip(),
                        officer_id=officer_id
                    )
                    
                    if success:
                        st.success(f"Dossier {tid} successfully updated to status: {decision.upper()}.")
                        st.session_state.review_tid = None
                        st.rerun()
                    else:
                        st.error("Failed to commit decision to the database.")
            
            if c_btn2.form_submit_button("CLOSE DOSSIER REVIEW", use_container_width=True):
                st.session_state.review_tid = None
                st.rerun()

    # ── TAB 2: PROCESSED CASES ──
    with tab2:
        processed = [tid for tid, c in complaints.items() if c.get("status", "pending").lower() in ["approve", "approved", "solve", "solved", "reject", "rejected"]]
        
        if not processed:
            st.info("No processed cases logged.")
        else:
            for tid in processed:
                c = complaints[tid]
                d = decisions.get(tid, {})
                status_text = c.get("status", "processed").upper()
                
                with st.expander(f"Case {tid} | {c.get('complaint_reason')} | {status_text}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Complainant:** {c.get('full_name')} (Anonymous: {c.get('anonymous')})")
                        st.write(f"**Email:** {c.get('email')}")
                        st.write(f"**Description:** {c.get('description')}")
                    with c2:
                        st.write(f"**Processed Officer:** `{d.get('officer_id', 'N/A')}`")
                        st.write(f"**Remarks:** *\"{d.get('notes', 'N/A')}\"*")
                        st.write(f"**Action Date:** {d.get('decided_at', 'N/A')[:16]}")

    # ── TAB 3: SYSTEM AUDIT LOGS ──
    with tab3:
        st.markdown("### 📋 SECURITY AUDIT TRAIL LOGS")
        st.write("Live logging of all security-sensitive operations, state changes, and authentication requests.")
        
        logs = db_service.get_audit_logs()
        if not logs:
            st.info("No audit trails logged in this session.")
        else:
            # Display logs in reverse order (most recent first)
            for log in reversed(logs):
                timestamp = log.get("timestamp", log.get("created_at", "N/A"))[:19].replace("T", " ")
                details_json = json.dumps(log.get("details", {}))
                
                action = log.get("action", "").upper()
                bg_color = "rgba(16, 185, 129, 0.1)"
                border_color = "rgba(16, 185, 129, 0.3)"
                
                if "FAILED" in action or "UNAUTHORIZED" in action:
                    bg_color = "rgba(239, 68, 68, 0.1)"
                    border_color = "rgba(239, 68, 68, 0.3)"
                elif "UPDATE" in action or "DECIDE" in action:
                    bg_color = "rgba(59, 130, 246, 0.1)"
                    border_color = "rgba(59, 130, 246, 0.3)"
                    
                st.markdown(f"""
                <div style="background: {bg_color}; border: 1px solid {border_color}; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8;">
                        <span>🕒 {timestamp} | Log ID: <code>{log.get('id')}</code></span>
                        <span style="font-weight: bold;">User Node: <code>{log.get('user_id')}</code></span>
                    </div>
                    <div style="margin-top: 5px; font-size: 0.95rem;">
                        <strong>Action:</strong> <span style="color: #3b82f6;">{action}</span> | 
                        <strong>Target:</strong> <code>{log.get('resource_type')}/{log.get('resource_id')}</code>
                    </div>
                    <div style="margin-top: 5px; font-size: 0.85rem; color: #cbd5e1; font-family: monospace; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px;">
                        Details: {details_json}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 4: AI AUTOMATION ──
    with tab4:
        st.subheader("🤖 AI AUTOMATION & DISPATCH CENTER")
        st.write("Leverage generative models to draft and dispatch legally compliant email updates to citizens.")
        
        processed_tids = list(decisions.keys())
        if not processed_tids:
            st.warning("No cases are currently processed to generate communications.")
        else:
            sel_tid = st.selectbox("Select Case Node to Notify:", processed_tids)
            if sel_tid:
                c = complaints.get(sel_tid)
                d = decisions.get(sel_tid)
                st.markdown("---")
                db_email = c.get('email', '')
                victim_email = st.text_input("Recipient Citizen Email:", value=db_email)
                
                if st.button("🪄 GENERATE SECURE AI EMAIL DRAFT"):
                    with st.spinner("AI Synthesizing professional dispatch..."):
                        draft = draft_ai_email(c, d['decision'], d['notes'])
                        st.session_state.ai_draft = draft
                
                if st.session_state.get('ai_draft'):
                    final = st.text_area("Review generated official copy:", value=st.session_state.ai_draft, height=350)
                    if st.button("📧 DISPATCH ENCRYPTED EMAIL", type="primary", use_container_width=True):
                        if not victim_email: 
                            st.error("Recipient email is required to send notification.")
                        else:
                            with st.spinner("Dispatching SMTP transmission..."):
                                success, err = send_case_update_email(victim_email, sel_tid, d['decision'], final)
                                if success: 
                                    st.success("Official email transmission dispatched successfully.")
                                    st.session_state.ai_draft = None
                                    # Audit log
                                    db_service.create_audit_log(
                                        user_id=officer_id,
                                        action="DISPATCH_CASE_EMAIL",
                                        resource_type="complaint",
                                        resource_id=sel_tid,
                                        details={"recipient": victim_email}
                                    )
                                else: 
                                    st.error(f"Transmission failed: {err}")

if __name__ == "__main__":
    render_officer_panel()
