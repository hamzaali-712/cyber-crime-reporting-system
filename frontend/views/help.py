"""
Cyber Crime Reporting System - Help & Support Page

Page for help and support information.
"""

import streamlit as st
from components import FAQSection

def render_help_page():
    """Render the help and support page."""
    st.header("Help & Support")

    # Emergency contacts
    st.subheader("🚨 Emergency Contacts")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Pakistan Police**")
        st.write("**Dial:** 15")
        st.write("*Immediate emergency response*")

    with col2:
        st.write("**FIA Cybercrime Wing**")
        st.write("**Contact:** Local FIA office")
        st.write("*Federal Investigation Agency*")

    with col3:
        st.write("**NCIA**")
        st.write("**National Cybercrime Investigation Agency**")
        st.write("*Specialized cybercrime unit*")

    st.markdown("---")

    # Victim support
    st.subheader("💙 Victim Support")

    st.write("""
    If you're a victim of cybercrime, remember:

    **Immediate Actions:**
    1. **Preserve Evidence** - Don't delete anything
    2. **Document Everything** - Take screenshots and notes
    3. **Report Immediately** - Time is critical
    4. **Seek Support** - You're not alone

    **Evidence to Preserve:**
    - Suspicious emails and messages
    - Transaction records
    - Screenshots of incidents
    - URLs and web addresses
    - Dates and times of occurrences
    """)

    # Support services
    st.subheader("🏥 Support Services")

    services = [
        {"name": "Cybercrime Helpline", "contact": "15", "description": "24/7 emergency support"},
        {"name": "Victim Support Center", "contact": "Local police", "description": "Counseling and guidance"},
        {"name": "Legal Aid Society", "contact": "Provincial offices", "description": "Free legal assistance"},
        {"name": "Digital Security Training", "contact": "NCIA website", "description": "Prevention education"}
    ]

    for service in services:
        with st.expander(f"{service['name']} - {service['contact']}"):
            st.write(service['description'])

    st.markdown("---")

    # FAQ section
    st.subheader("❓ Frequently Asked Questions")
    FAQSection.render_faqs()

    # Contact form
    st.markdown("---")
    st.subheader("📧 Contact Us")

    with st.form("contact_form"):
        st.write("Have a question? Send us a message.")

        name = st.text_input("Name")
        email = st.text_input("Email")
        subject = st.selectbox("Subject", ["General Inquiry", "Technical Issue", "Legal Question", "Other"])
        message = st.text_area("Message")

        submitted = st.form_submit_button("Send Message")

        if submitted:
            if not name or not email or not message:
                st.error("Please fill in all required fields.")
            else:
                st.success("Message sent successfully! We'll get back to you soon.")

if __name__ == "__main__":
    render_help_page()