"""
Cyber Crime Reporting System - Law Guide Page

Page for accessing cybercrime laws and regulations.
"""

import streamlit as st
from components import LawGuide

def render_law_guide_page():
    """Render the cyber law guide page."""
    st.header("Pakistan Cyber Crime Rule Book")

    st.markdown("""
    Access Pakistan's Prevention of Electronic Crimes Act (PECA) 2016 and related laws.
    Find applicable sections for your complaint and understand legal protections.
    """)

    # AI Legal Assistant (mock)
    st.subheader("🤖 AI Legal Assistant")
    complaint_type = st.selectbox(
        "Describe your situation:",
        ["", "Hacking", "Phishing", "Cyberstalking", "Online Harassment",
         "Data Theft", "Financial Fraud", "Child Exploitation", "Other"]
    )

    if complaint_type and st.button("Get Legal Guidance"):
        st.info(f"**Applicable Law:** Based on {complaint_type} incidents, refer to PECA Section 13-16 for unauthorized access and hacking-related offenses.")

    st.markdown("---")

    # Law search component
    LawGuide.render_law_search()

    # Additional resources
    st.markdown("---")
    st.subheader("Additional Resources")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**📚 Full PECA 2016 Text**")
        st.write("Read the complete Prevention of Electronic Crimes Act.")

    with col2:
        st.write("**📞 Legal Consultation**")
        st.write("Contact legal experts for personalized advice.")

    st.warning("""
    **Disclaimer:** This information is for educational purposes.
    Consult qualified legal professionals for specific legal advice.
    """)

if __name__ == "__main__":
    render_law_guide_page()