"""
Cyber Crime Reporting System - Tracking Page

Page for tracking complaint status.
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR / "frontend") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "frontend"))

# Database files
COMPLAINTS_FILE = BASE_DIR / "backend" / "data" / "complaints.json"
DECISIONS_FILE = BASE_DIR / "backend" / "data" / "officer_decisions.json"

def load_complaints():
    """Load complaints database."""
    if os.path.exists(COMPLAINTS_FILE):
        try:
            with open(COMPLAINTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def load_decisions():
    """Load officer decisions database."""
    if os.path.exists(DECISIONS_FILE):
        try:
            with open(DECISIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def render_tracking_page(set_page_config: bool = True):
    """Render the complaint tracking page."""
    if set_page_config:
        st.set_page_config(
            page_title="Track Complaint - Cyber Crime System",
            page_icon="📍",
            layout="wide"
        )
    
    # Custom CSS
    css = """
    <style>
    .tracking-card {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
    }
    .pending-status {
        background: #fef08a;
        color: #854d0e;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .approved-status {
        background: #dcfce7;
        color: #166534;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .rejected-status {
        background: #fee2e2;
        color: #b91c1c;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    st.header("📍 Track Your Complaint")

    st.write("""
    Enter your tracking ID below to check the status of your cybercrime complaint.
    Your tracking ID was provided when you submitted your complaint.
    """)

    # Search for complaint
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tracking_id = st.text_input(
            "Tracking ID",
            placeholder="CCRS-PK-2026-XXXXXXXX"
        )
    
    with col2:
        st.write("")
        search_btn = st.button("Search", type="primary")

    if search_btn and tracking_id:
        complaints = load_complaints()
        decisions = load_decisions()
        
        if tracking_id in complaints:
            complaint = complaints[tracking_id]
            decision = decisions.get(tracking_id)
            
            st.markdown("---")
            st.subheader("✅ Complaint Found")
            
            st.markdown('<div class="tracking-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Tracking ID:** {tracking_id}")
                st.write(f"**Complaint Type:** {complaint.get('complaint_reason')}")
                st.write(f"**Incident Date:** {complaint.get('incident_date')}")
                st.write(f"**Location:** {complaint.get('location')}")
            
            with col2:
                if not complaint.get('anonymous'):
                    st.write(f"**Name:** {complaint.get('full_name', 'N/A')}")
                    st.write(f"**Phone:** {complaint.get('phone', 'N/A')}")
                else:
                    st.write("**Type:** Anonymous Report")
            
            st.markdown("---")
            
            # Status
            st.subheader("📊 Complaint Status")
            
            if decision:
                if "Approve" in decision.get("decision", ""):
                    st.markdown('<div class="approved-status">✅ APPROVED - CASE SOLVED</div>', unsafe_allow_html=True)
                    st.info(f"**Officer Decision:** {decision.get('decision')}")
                    st.info(f"**Notes:** {decision.get('notes')}")
                    st.info(f"**Decided By:** {decision.get('officer_id')}")
                    st.info(f"**Date:** {decision.get('decided_at')}")
                else:
                    st.markdown('<div class="rejected-status">❌ REJECTED - INVALID/INCOMPLETE</div>', unsafe_allow_html=True)
                    st.warning(f"**Officer Decision:** {decision.get('decision')}")
                    st.warning(f"**Reason:** {decision.get('notes')}")
                    st.warning(f"**Decided By:** {decision.get('officer_id')}")
                    st.warning(f"**Date:** {decision.get('decided_at')}")
            else:
                st.markdown('<div class="pending-status">⏳ PENDING REVIEW</div>', unsafe_allow_html=True)
                st.info("Your complaint is currently being reviewed by our law enforcement team. Please check back later for updates.")
            
            st.markdown("---")
            st.subheader("📝 Your Complaint Details")
            st.write(f"**Description:** {complaint.get('description')}")
            st.write(f"**Evidence Files:** {complaint.get('evidence_count', 0)} file(s)")
            st.write(f"**Submitted:** {complaint.get('submitted_at')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.error(f"❌ Tracking ID '{tracking_id}' not found in the system.")
            st.info("Please check if you entered the correct tracking ID.")
    elif search_btn:
        st.error("Please enter a tracking ID to search.")

    # Additional information
    st.markdown("---")
    st.subheader("❓ Need Help?")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Lost your tracking ID?**")
        st.write("Contact the cybercrime helpline for assistance.")

    with col2:
        st.write("**Status not updating?**")
        st.write("Allow 24-48 hours for initial processing.")

    st.info("""
    **Important Notes:**
    - Status updates may take time during peak periods
    - All complaints are investigated thoroughly
    - You may be contacted for additional information
    - Keep your tracking ID secure and confidential
    """)

if __name__ == "__main__":
    render_tracking_page()