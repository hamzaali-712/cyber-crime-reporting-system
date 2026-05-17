"""
Cyber Crime Reporting System - Tracking Page
Modern Premium Version using Centralized DB Service
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Ensure local path imports work
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.services.database_service import db_service

def render_tracking_page(set_page_config: bool = True):
    if set_page_config:
        st.set_page_config(page_title="Track Complaint Status - NCIA", page_icon="📍", layout="wide")
    
    st.markdown("## 📍 CASE TRACKING SYSTEM")
    st.write("Track the real-time progress and investigation remarks of your filed complaint.")

    # Search Box Area
    col_input, col_btn = st.columns([3, 1])
    
    # Auto-fill if coming from a recent submission
    default_id = st.session_state.get('last_tracking_id', "")
    
    with col_input:
        tracking_id = st.text_input(
            "Enter Case Tracking ID",
            value=default_id,
            placeholder="E.g., CCRS-PK-2026-XXXXXXXX"
        )

    with col_btn:
        st.write("")
        st.write("")
        search_btn = st.button("SEARCH COMPLAINT", type="primary", use_container_width=True)

    if search_btn and tracking_id:
        # Centralized DB Service Call
        c = db_service.get_complaint(tracking_id)
        d = db_service.get_decision(tracking_id)
        
        if c:
            st.markdown("---")
            st.markdown(f"### ✅ Complaint Details Found: `{tracking_id}`")
            
            # Tracking Card
            st.markdown('<div class="tracking-card cyber-glow">', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Cybercrime Category:** {c.get('complaint_reason')}")
                st.write(f"**Date of Occurrence:** {c.get('incident_date')}")
                st.write(f"**Incident Location/Source:** {c.get('location')}")
            with c2:
                if c.get('anonymous'):
                    st.write("**Complainant Name:** [REPORTED ANONYMOUSLY]")
                else:
                    st.write(f"**Complainant Name:** {c.get('full_name')}")
                st.write(f"**Submission Date:** {c.get('submitted_at')[:16]}")

            st.markdown("---")
            
            # Status Indicator
            st.subheader("📊 INVESTIGATION STATUS")
            
            # Read status directly from the synchronized complaint object or fallback to decision
            status = c.get("status", "pending").lower()
            
            if status == "solve" or status == "solved":
                st.markdown('<div class="status-pill status-solved" style="display:inline-block; padding: 5px 15px; font-size:1rem;">CASE RESOLVED</div>', unsafe_allow_html=True)
                st.success("Your case has been thoroughly investigated and marked as RESOLVED.")
            elif status == "approve" or status == "approved" or status == "under investigation":
                st.markdown('<div class="status-pill status-approved" style="display:inline-block; padding: 5px 15px; font-size:1rem;">UNDER ACTIVE INVESTIGATION</div>', unsafe_allow_html=True)
                st.info("The NCIA cybercrime branch has approved your case and placed it under active investigation.")
            elif status == "reject" or status == "rejected":
                st.markdown('<div class="status-pill status-pending" style="display:inline-block; padding: 5px 15px; font-size:1rem; border-color:#ef4444; color:#ef4444; background:rgba(239,68,68,0.1);">COMPLAINT REJECTED</div>', unsafe_allow_html=True)
                st.error("This case has been closed due to insufficient details or evidence.")
            else:
                st.markdown('<div class="status-pill status-pending" style="display:inline-block; padding: 5px 15px; font-size:1rem;">PENDING REVIEW</div>', unsafe_allow_html=True)
                st.warning("Your complaint is currently in the review queue. An analyst will verify your submitted details shortly.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if d:
                notes = d.get("notes", "No additional investigator remarks yet.")
                st.markdown(f"**Investigating Officer Remarks:** *\"{notes}\"*")
                st.markdown(f"**Last Updated Time:** {d.get('decided_at')[:16]}")
            else:
                st.write("**Officer Remarks:** *\"Pending case assignment and details verification.\"*")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.error(f"❌ Case ID '{tracking_id}' was not found in our secure central database. Please make sure there are no typos.")
    
    elif search_btn:
        st.warning("Please enter a valid tracking ID.")

if __name__ == "__main__":
    render_tracking_page()