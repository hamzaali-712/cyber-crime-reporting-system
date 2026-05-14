"""
Officer Panel - View and Manage Cybercrime Reports
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Ensure local frontend imports work properly
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from views.officer_login import is_officer_logged_in, get_current_officer_id, logout_officer

# Database file for complaints
COMPLAINTS_FILE = BASE_DIR / "backend" / "data" / "complaints.json"
OFFICER_DECISIONS_FILE = BASE_DIR / "backend" / "data" / "officer_decisions.json"

def load_complaints():
    """Load complaints database."""
    if os.path.exists(COMPLAINTS_FILE):
        try:
            with open(COMPLAINTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_complaints(complaints):
    """Save complaints to database."""
    os.makedirs(COMPLAINTS_FILE.parent, exist_ok=True)
    with open(COMPLAINTS_FILE, 'w') as f:
        json.dump(complaints, f, indent=2, default=str)

def load_decisions():
    """Load officer decisions database."""
    if os.path.exists(OFFICER_DECISIONS_FILE):
        try:
            with open(OFFICER_DECISIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_decisions(decisions):
    """Save officer decisions to database."""
    os.makedirs(OFFICER_DECISIONS_FILE.parent, exist_ok=True)
    with open(OFFICER_DECISIONS_FILE, 'w') as f:
        json.dump(decisions, f, indent=2, default=str)

def render_officer_panel(set_page_config: bool = True):
    """Render the officer panel."""
    if set_page_config:
        st.set_page_config(
            page_title="Officer Panel - Cyber Crime System",
            page_icon="👮",
            layout="wide"
        )
    
    # Check authentication
    if not is_officer_logged_in():
        st.error("❌ Please login first.")
        if st.button("Go to Login"):
            st.session_state.current_page = "officer_login"
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            elif hasattr(st, "rerun"):
                st.rerun()
        return
    
    officer_id = get_current_officer_id()
    
    # Custom CSS
    st.markdown("""
    <style>
    .header-box {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .complaint-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    .pending-badge {
        background: #fef08a;
        color: #854d0e;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .approved-badge {
        background: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .rejected-badge {
        background: #fee2e2;
        color: #b91c1c;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with logout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="header-box">
            <h1>👮 Officer Panel</h1>
            <p>Manage and Process Cybercrime Reports</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.write("")
        st.write("")
        if st.button("🚪 Logout"):
            logout_officer()
            st.success("Logged out successfully!")
            import time
            time.sleep(1)
            st.session_state.current_page = "officer_login"
            if hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
            elif hasattr(st, "rerun"):
                st.rerun()
    
    # Officer info
    st.info(f"**Officer ID:** {officer_id}")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Pending Reports", "✅ Approved Cases", "🛠️ Solved Cases", "❌ Rejected Cases", "📊 Statistics"])
    
    complaints = load_complaints()
    decisions = load_decisions()
    
    # Pending Reports Tab
    with tab1:
        st.subheader("Pending Reports Awaiting Review")
        
        pending_complaints = []
        for tracking_id, complaint in complaints.items():
            if not decisions.get(tracking_id):  # No decision made yet
                pending_complaints.append((tracking_id, complaint))
        
        if not pending_complaints:
            st.info("✅ No pending reports. All cases have been reviewed!")
        else:
            for tracking_id, complaint in pending_complaints:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="complaint-card">
                            <h4>📌 {complaint.get('complaint_reason', 'Unknown')}</h4>
                            <p><strong>Tracking ID:</strong> {tracking_id}</p>
                            <p><strong>Date:</strong> {complaint.get('incident_date', 'N/A')}</p>
                            <p><strong>Location:</strong> {complaint.get('location', 'N/A')}</p>
                            <p><strong>Status:</strong> <span class="pending-badge">PENDING</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("👁️ Review", key=f"review_{tracking_id}"):
                            st.session_state.selected_complaint = tracking_id
                            st.session_state.selected_complaint_data = complaint
                            if hasattr(st, "experimental_rerun"):
                                st.experimental_rerun()
                            elif hasattr(st, "rerun"):
                                st.rerun()
    
    # Review Complaint Detail
    if st.session_state.get("selected_complaint"):
        st.markdown("---")
        st.subheader("📖 Complaint Details")
        
        tracking_id = st.session_state.selected_complaint
        complaint = st.session_state.selected_complaint_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Tracking ID:** {tracking_id}")
            st.write(f"**Complaint Type:** {complaint.get('complaint_reason')}")
            st.write(f"**Incident Date:** {complaint.get('incident_date')}")
            st.write(f"**Location:** {complaint.get('location')}")
        
        with col2:
            if not complaint.get('anonymous'):
                st.write(f"**Complainant:** {complaint.get('full_name', 'N/A')}")
                st.write(f"**Phone:** {complaint.get('phone', 'N/A')}")
                st.write(f"**CNIC:** {complaint.get('cnic', 'N/A')}")
            else:
                st.write("**Report Type:** Anonymous")
        
        st.markdown("---")
        st.subheader("📝 Description")
        st.write(complaint.get('description'))
        
        # Officer Decision Section
        st.markdown("---")
        st.subheader("🔍 Officer Decision")
        
        decision = st.radio(
            "Make a decision:",
            ["Select...", "Approve - Case is Valid/Under Investigation", "Solve - Case Solved Successfully", "Reject - Case Invalid/Incomplete"]
        )
        
        if decision != "Select...":
            notes = st.text_area(
                "Investigation Notes",
                placeholder="Add your notes about this case..."
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Submit Decision", type="primary"):
                    if not notes:
                        st.error("Please add investigation notes.")
                    else:
                        # Save decision
                        decision_data = {
                            "officer_id": officer_id,
                            "tracking_id": tracking_id,
                            "decision": decision,
                            "notes": notes,
                            "decided_at": datetime.now().isoformat()
                        }
                        
                        all_decisions = load_decisions()
                        all_decisions[tracking_id] = decision_data
                        save_decisions(all_decisions)
                        
                        # Update complaint status
                        all_complaints = load_complaints()
                        if "Approve" in decision:
                            status = "approved"
                        elif "Solve" in decision:
                            status = "solved"
                        else:
                            status = "rejected"
                            
                        all_complaints[tracking_id]["status"] = status
                        all_complaints[tracking_id]["officer_decision"] = decision
                        all_complaints[tracking_id]["decided_by"] = officer_id
                        save_complaints(all_complaints)
                        
                        st.success("✅ Decision recorded successfully!")
                        st.balloons()
                        
                        import time
                        time.sleep(2)
                        st.session_state.selected_complaint = None
                        if hasattr(st, "experimental_rerun"):
                            st.experimental_rerun()
                        elif hasattr(st, "rerun"):
                            st.rerun()
            
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.selected_complaint = None
                    if hasattr(st, "experimental_rerun"):
                        st.experimental_rerun()
                    elif hasattr(st, "rerun"):
                        st.rerun()
    with tab2:
        st.subheader("✅ Approved Cases - Under Investigation")
        
        approved_complaints = []
        for tracking_id, complaint in complaints.items():
            decision = decisions.get(tracking_id)
            if decision and "Approve" in decision.get("decision", ""):
                approved_complaints.append((tracking_id, complaint, decision))
        
        if not approved_complaints:
            st.info("No approved cases yet.")
        else:
            for tracking_id, complaint, decision in approved_complaints:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="complaint-card" style="border-left: 4px solid #10b981;">
                            <h4>✅ {complaint.get('complaint_reason')}</h4>
                            <p><strong>Tracking ID:</strong> {tracking_id}</p>
                            <p><strong>Status:</strong> <span class="approved-badge">APPROVED</span></p>
                            <p><strong>Officer:</strong> {decision.get('officer_id')}</p>
                            <p><strong>Decided On:</strong> {decision.get('decided_at', 'N/A')}</p>
                            <p><strong>Notes:</strong> {decision.get('notes', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("🔄 Update Status", key=f"update_{tracking_id}"):
                            st.session_state.selected_complaint = tracking_id
                            st.session_state.selected_complaint_data = complaint
                            if hasattr(st, "experimental_rerun"):
                                st.experimental_rerun()
                            elif hasattr(st, "rerun"):
                                st.rerun()
                                
    # Solved Cases Tab
    with tab3:
        st.subheader("🛠️ Solved Cases - Successfully Completed")
        
        solved_complaints = []
        for tracking_id, complaint in complaints.items():
            decision = decisions.get(tracking_id)
            if decision and "Solve" in decision.get("decision", ""):
                solved_complaints.append((tracking_id, complaint, decision))
        
        if not solved_complaints:
            st.info("No solved cases yet.")
        else:
            for tracking_id, complaint, decision in solved_complaints:
                st.markdown(f"""
                <div class="complaint-card" style="border-left: 4px solid #3b82f6;">
                    <h4>🛠️ {complaint.get('complaint_reason')}</h4>
                    <p><strong>Tracking ID:</strong> {tracking_id}</p>
                    <p><strong>Status:</strong> <span class="approved-badge" style="background:#bfdbfe;color:#1e3a8a;">SOLVED</span></p>
                    <p><strong>Officer:</strong> {decision.get('officer_id')}</p>
                    <p><strong>Decided On:</strong> {decision.get('decided_at', 'N/A')}</p>
                    <p><strong>Notes:</strong> {decision.get('notes', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Rejected Cases Tab
    with tab4:
        st.subheader("❌ Rejected Cases - Invalid/Incomplete")
        
        rejected_complaints = []
        for tracking_id, complaint in complaints.items():
            decision = decisions.get(tracking_id)
            if decision and "Reject" in decision.get("decision", ""):
                rejected_complaints.append((tracking_id, complaint, decision))
        
        if not rejected_complaints:
            st.info("No rejected cases yet.")
        else:
            for tracking_id, complaint, decision in rejected_complaints:
                st.markdown(f"""
                <div class="complaint-card" style="border-left: 4px solid #ef4444;">
                    <h4>❌ {complaint.get('complaint_reason')}</h4>
                    <p><strong>Tracking ID:</strong> {tracking_id}</p>
                    <p><strong>Status:</strong> <span class="rejected-badge">REJECTED</span></p>
                    <p><strong>Officer:</strong> {decision.get('officer_id')}</p>
                    <p><strong>Decided On:</strong> {decision.get('decided_at', 'N/A')}</p>
                    <p><strong>Reason:</strong> {decision.get('notes', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Statistics Tab
    with tab5:
        st.subheader("📊 Case Statistics")
        
        total_cases = len(complaints)
        pending_cases = len([tracking_id for tracking_id in complaints.keys() if tracking_id not in decisions])
        approved_cases = len([d for d in decisions.values() if "Approve" in d.get("decision", "")])
        solved_cases = len([d for d in decisions.values() if "Solve" in d.get("decision", "")])
        rejected_cases = len([d for d in decisions.values() if "Reject" in d.get("decision", "")])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Cases", total_cases)
        
        with col2:
            st.metric("Pending Review", pending_cases)
        
        with col3:
            st.metric("Approved", approved_cases)
            
        with col4:
            st.metric("Solved", solved_cases)
        
        with col5:
            st.metric("Rejected", rejected_cases)
        
        st.markdown("---")
        st.subheader("📈 Case Status Breakdown")
        
        status_data = {
            "Pending": pending_cases,
            "Approved": approved_cases,
            "Solved": solved_cases,
            "Rejected": rejected_cases
        }
        
        st.bar_chart(status_data)

if __name__ == "__main__":
    # Initialize session state
    if "officer_logged_in" not in st.session_state:
        st.session_state.officer_logged_in = False
    
    if "selected_complaint" not in st.session_state:
        st.session_state.selected_complaint = None
    
    render_officer_panel()
