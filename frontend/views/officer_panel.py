"""
Officer Panel - Case Management Dashboard
Includes Robust Evidence Discovery.
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

def get_actual_evidence_files(tracking_id):
    """Scans the physical directory for evidence files to ensure 100% accuracy."""
    case_dir = EVIDENCE_BASE_DIR / tracking_id
    if case_dir.exists() and case_dir.is_dir():
        return [f for f in os.listdir(case_dir) if os.path.isfile(case_dir / f)]
    return []

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
                    st.markdown(f'<div class="complaint-card"><h4 style="margin:5px 0;">{c.get("complaint_reason")}</h4><p>ID: {tid}</p></div>', unsafe_allow_html=True)
                with col2:
                    if st.button("REVIEW", key=f"rev_{tid}"):
                        st.session_state.review_tid = tid
                        st.rerun()

    if st.session_state.get('review_tid'):
        tid = st.session_state.review_tid
        c = complaints[tid]
        st.markdown("---")
        st.subheader(f"🔍 CASE DOSSIER: {tid}")
        
        # Details
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 👤 Citizen Information")
            st.write(f"**Name:** {c.get('full_name')}")
            st.write(f"**CNIC:** {c.get('cnic')}")
        with c2:
            st.markdown("#### 🛰️ Incident Info")
            st.write(f"**Crime Type:** {c.get('complaint_reason')}")
            st.write(f"**Submission Date:** {c.get('submitted_at')}")

        st.markdown("#### 📄 Description")
        st.info(c.get('description'))

        # ── Robust Evidence Section ──
        st.markdown("#### 📁 EVIDENCE REPOSITORY")
        
        # Scan filesystem directly instead of relying on JSON metadata
        physical_files = get_actual_evidence_files(tid)
        
        if not physical_files:
            st.warning("No physical evidence detected in the secure repository for this case.")
            st.info("If you just uploaded evidence, please ensure the submission completed successfully.")
        else:
            st.success(f"Detected {len(physical_files)} evidence files.")
            cols = st.columns(min(len(physical_files), 4))
            for i, fname in enumerate(physical_files):
                with cols[i % 4]:
                    fpath = EVIDENCE_BASE_DIR / tid / fname
                    with open(fpath, "rb") as f:
                        st.download_button(
                            label=f"📥 {fname}",
                            data=f,
                            file_name=fname,
                            key=f"robust_dl_{tid}_{i}"
                        )
                    if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                        st.image(str(fpath), use_container_width=True)

        with st.form("action_form"):
            st.markdown("#### ⚡ Operational Decision")
            decision = st.selectbox("Status:", ["Approve", "Solve", "Reject"])
            notes = st.text_area("Officer Remarks:")
            if st.form_submit_button("SUBMIT DECISION", use_container_width=True):
                decisions[tid] = {"officer_id": officer_id, "decision": decision, "notes": notes, "timestamp": datetime.now().isoformat()}
                save_json(OFFICER_DECISIONS_FILE, decisions)
                st.session_state.review_tid = None
                st.rerun()
            if st.form_submit_button("CLOSE", use_container_width=True):
                st.session_state.review_tid = None
                st.rerun()

    with tab2:
        for tid, d in decisions.items():
            c = complaints.get(tid, {})
            st.markdown(f'<div class="complaint-card"><h4 style="margin:5px 0;">{c.get("complaint_reason")}</h4><p>ID: {tid}</p></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    render_officer_panel()
