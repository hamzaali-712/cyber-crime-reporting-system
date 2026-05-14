"""
Officer Panel - View and Manage Cybercrime Reports
Modern Premium Version
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Ensure local frontend imports work properly
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from views.officer_login import is_officer_logged_in, get_current_officer_id, logout_officer
from backend.utils.email_service import send_case_update_email

logger = logging.getLogger(__name__)

# Database files
COMPLAINTS_FILE = ROOT_DIR / "backend" / "data" / "complaints.json"
OFFICER_DECISIONS_FILE = ROOT_DIR / "backend" / "data" / "officer_decisions.json"

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
    return {}

def save_json(file_path, data):
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def render_officer_panel(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Officer Panel - Cyber System", page_icon="👮", layout="wide")
    
    if not is_officer_logged_in():
        st.error("❌ UNAUTHORIZED ACCESS DETECTED. PLEASE AUTHENTICATE.")
        if st.button("RETURN TO LOGIN"):
            st.session_state.current_page = "officer_login"
            st.rerun()
        return
    
    officer_id = get_current_officer_id()

    # Header with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"## 👮 COMMAND CENTER: {officer_id}")
    with col2:
        if st.button("🚪 TERMINATE SESSION", use_container_width=True):
            logout_officer()
            st.rerun()

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 PENDING QUEUE", 
        "✅ ACTIVE CASES", 
        "🛠️ SOLVED ARCHIVE", 
        "❌ REJECTED FILES", 
        "📊 ANALYTICS"
    ])
    
    complaints = load_json(COMPLAINTS_FILE)
    decisions = load_json(OFFICER_DECISIONS_FILE)
    
    # ── Tab 1: Pending Reports ──
    with tab1:
        st.subheader("Reports Awaiting Operational Decision")
        pending = [(tid, c) for tid, c in complaints.items() if tid not in decisions]
        
        if not pending:
            st.info("🎯 All reports processed. Operational queue is empty.")
        else:
            for tid, c in pending:
                with st.container():
                    col_info, col_act = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"""
                        <div class="complaint-card cyber-glow">
                            <h4>{c.get('complaint_reason', 'UNKNOWN')}</h4>
                            <p><strong>NODE ID:</strong> {tid}</p>
                            <p><strong>TIMESTAMP:</strong> {c.get('submitted_at', 'N/A')}</p>
                            <p><span class="pending-badge">STATUS: PENDING</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_act:
                        st.write("")
                        if st.button("🔍 ANALYZE", key=f"rev_{tid}"):
                            st.session_state.selected_complaint = tid
                            st.session_state.selected_complaint_data = c
                            st.rerun()

    # ── Review Detail Modal Logic ──
    if st.session_state.get("selected_complaint"):
        st.markdown("---")
        st.markdown("### 🔍 CASE ANALYSIS MODULE")
        
        tid = st.session_state.selected_complaint
        c = st.session_state.selected_complaint_data
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**ID:** {tid}")
            st.write(f"**Category:** {c.get('complaint_reason')}")
            st.write(f"**Date:** {c.get('incident_date')}")
        with col2:
            st.write(f"**Complainant:** {c.get('full_name', 'ANONYMOUS')}")
            st.write(f"**Contact:** {c.get('phone', 'N/A')}")
            st.write(f"**Email:** {c.get('email', 'N/A')}") # Assuming email might be captured

        st.markdown("**Incident Log:**")
        st.info(c.get('description'))
        
        st.markdown("#### ⚡ OPERATIONAL DECISION")
        decision = st.selectbox(
            "Select Action Path:",
            ["Select...", "Approve - Initiate Investigation", "Solve - Close Successfully", "Reject - Invalid Entry"]
        )
        
        if decision != "Select...":
            notes = st.text_area("Operational Notes:", placeholder="Provide details for the citizen and internal logs...")
            
            c_email = c.get('email') # Check if email exists
            if not c_email:
                c_email = st.text_input("User Email (for notification):", placeholder="user@example.com")

            col_sub, col_can = st.columns(2)
            with col_sub:
                if st.button("🚀 SUBMIT & NOTIFY", type="primary"):
                    if not notes:
                        st.error("NOTES REQUIRED FOR DECISION LOG.")
                    else:
                        # 1. Save Decision
                        d_data = {
                            "officer_id": officer_id,
                            "tracking_id": tid,
                            "decision": decision,
                            "notes": notes,
                            "decided_at": datetime.now().isoformat()
                        }
                        all_d = load_json(OFFICER_DECISIONS_FILE)
                        all_d[tid] = d_data
                        save_json(OFFICER_DECISIONS_FILE, all_d)
                        
                        # 2. Update Complaint
                        all_c = load_json(COMPLAINTS_FILE)
                        status_map = {"Approve": "approved", "Solve": "solved", "Reject": "rejected"}
                        new_status = next((v for k, v in status_map.items() if k in decision), "pending")
                        
                        all_c[tid]["status"] = new_status
                        save_json(COMPLAINTS_FILE, all_c)
                        
                        # 3. Email Notification
                        if c_email:
                            with st.spinner("Sending secure notification..."):
                                send_case_update_email(c_email, tid, new_status, notes)
                        
                        st.success(f"✅ CASE {tid} UPDATED. NOTIFICATION DISPATCHED.")
                        import time
                        time.sleep(2)
                        st.session_state.selected_complaint = None
                        st.rerun()
            
            with col_can:
                if st.button("❌ ABORT"):
                    st.session_state.selected_complaint = None
                    st.rerun()

    # ── Tab 2: Approved Cases ──
    with tab2:
        st.subheader("Active Investigations")
        for tid, c in complaints.items():
            d = decisions.get(tid)
            if d and "Approve" in d.get("decision", ""):
                st.markdown(f"""
                <div class="complaint-card" style="border-left: 6px solid var(--primary);">
                    <h4>✅ {c.get('complaint_reason')}</h4>
                    <p><strong>ID:</strong> {tid} | <strong>OFFICER:</strong> {d.get('officer_id')}</p>
                    <p><span class="approved-badge">STATUS: INVESTIGATING</span></p>
                    <p style="font-size:0.9rem; opacity:0.8;">{d.get('notes')}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("UPDATE STATUS", key=f"up_{tid}"):
                    st.session_state.selected_complaint = tid
                    st.session_state.selected_complaint_data = c
                    st.rerun()

    # ── Tab 3: Solved ──
    with tab3:
        for tid, c in complaints.items():
            d = decisions.get(tid)
            if d and "Solve" in d.get("decision", ""):
                st.markdown(f"""
                <div class="complaint-card" style="border-left: 6px solid var(--success);">
                    <h4>🛠️ {c.get('complaint_reason')}</h4>
                    <p><strong>ID:</strong> {tid} | <span class="solved-badge">RESOLVED</span></p>
                    <p style="font-size:0.9rem; opacity:0.8;">{d.get('notes')}</p>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 4: Rejected ──
    with tab4:
        for tid, c in complaints.items():
            d = decisions.get(tid)
            if d and "Reject" in d.get("decision", ""):
                st.markdown(f"""
                <div class="complaint-card" style="border-left: 6px solid var(--error);">
                    <h4>❌ {c.get('complaint_reason')}</h4>
                    <p><strong>ID:</strong> {tid} | <span class="rejected-badge">REJECTED</span></p>
                    <p style="font-size:0.9rem; opacity:0.8;">{d.get('notes')}</p>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 5: Stats ──
    with tab5:
        total = len(complaints)
        pend = len(pending)
        appr = len([x for x in decisions.values() if "Approve" in x.get('decision')])
        solv = len([x for x in decisions.values() if "Solve" in x.get('decision')])
        reje = len([x for x in decisions.values() if "Reject" in x.get('decision')])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL NODES", total)
        c2.metric("PENDING", pend)
        c3.metric("RESOLVED", solv)
        c4.metric("REJECTED", reje)
        
        st.bar_chart({"Pending": pend, "Active": appr, "Solved": solv, "Rejected": reje})

if __name__ == "__main__":
    render_officer_panel()
