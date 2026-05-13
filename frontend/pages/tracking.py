"""
Cyber Crime Reporting System - Tracking Page

Page for tracking complaint status.
"""

import streamlit as st
from components import StatusTracker

def render_tracking_page():
    """Render the complaint tracking page."""
    st.header("Track Your Complaint")

    st.write("""
    Enter your tracking ID below to check the status of your cybercrime complaint.
    Your tracking ID was provided when you submitted your complaint.
    """)

    # Render status tracker component
    StatusTracker.render_tracker()

    # Additional information
    st.markdown("---")
    st.subheader("Need Help?")

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