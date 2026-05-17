"""
Cyber Crime Reporting System - Citizen Portal
Separated, Dedicated, and Premium Citizen Hub (100% Secure)
"""

import streamlit as st
import os
import sys
import pathlib
from dotenv import load_dotenv
from datetime import datetime

# ── Path Setup ────────────────────────────────────────────────────────────────
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent
ROOT_DIR     = FRONTEND_DIR.parent

for _p in (str(ROOT_DIR), str(FRONTEND_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

load_dotenv()

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="National Cyber Crime Portal PK",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS Loader ─────────────────────────────────────────────────────────
def load_css():
    css_path = FRONTEND_DIR / "static" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session Management ────────────────────────────────────────────────────────
def initialize_session():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

def navigate_to(page_name: str):
    st.session_state.current_page = page_name
    st.rerun()

# ── Home Page Component ───────────────────────────────────────────────────────
def render_hero_home():
    # Hero Title with modern badge
    st.markdown("""
    <div class="hero-container">
        <span class="gov-badge">GOVERNMENT OF PAKISTAN - OFFICIAL PORTAL</span>
        <h1 class="hero-title">NATIONAL ELECTRONIC CRIME REPORTING PORTAL</h1>
        <p class="hero-subtitle">Secure, confidential, and rapid cyber investigation services under PECA 2016</p>
    </div>
    """, unsafe_allow_html=True)

    # Core Action Grid
    st.markdown("### ⚡ QUICK ACCESS CHANNELS")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="action-card cyber-glow">
            <div class="card-icon">📋</div>
            <h4>Report Cyber Crime</h4>
            <p>Submit secure, confidential, or anonymous digital evidence of electronic offenses.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("FILE NEW COMPLAINT", key="btn_go_report", use_container_width=True, type="primary"):
            navigate_to("report_form")

    with c2:
        st.markdown("""
        <div class="action-card cyber-glow">
            <div class="card-icon">📍</div>
            <h4>Track Complaint</h4>
            <p>Check the active investigation status and view official investigator updates.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("CHECK CASE STATUS", key="btn_go_track", use_container_width=True):
            navigate_to("tracking")

    with c3:
        st.markdown("""
        <div class="action-card cyber-glow">
            <div class="card-icon">📚</div>
            <h4>Cyber Law Guide</h4>
            <p>Read Pakistan's Prevention of Electronic Crimes Act (PECA) 2016 law repository.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("QUERY CYBER LAWS", key="btn_go_laws", use_container_width=True):
            navigate_to("law_guide")

    with c4:
        st.markdown("""
        <div class="action-card cyber-glow">
            <div class="card-icon">❓</div>
            <h4>Help & Support</h4>
            <p>Get emergency telephone support, counseling resources, and reporting protocols.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("GET VICTIM HELP", key="btn_go_help", use_container_width=True):
            navigate_to("help_support")

    st.markdown("<br><hr style='border: 1px solid rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)

    # Threat Monitor & Metrics Grid
    c_m1, c_m2 = st.columns([2, 1])
    
    with c_m1:
        st.markdown("### 🛰️ GLOBAL NCIA THREAT MONITOR")
        # Custom threat dashboard
        st.markdown("""
        <div class="threat-monitor-container">
            <div class="threat-stat-row">
                <span class="threat-label">🛡️ National Cyber Compliance State</span>
                <span class="threat-value val-green">PECA 2016 ACTIVE</span>
            </div>
            <div class="threat-stat-row">
                <span class="threat-label">🔒 Cryptographic Storage Channel</span>
                <span class="threat-value val-blue">AES-256 ENCRYPTED</span>
            </div>
            <div class="threat-stat-row">
                <span class="threat-label">🕵️ Complainant Privacy Isolation</span>
                <span class="threat-value val-green">FULLY OPERATIONAL</span>
            </div>
            <div class="threat-stat-row">
                <span class="threat-label">📬 Server Gateway Response Time</span>
                <span class="threat-value val-blue">14ms (OPTIMAL)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_m2:
        st.markdown("### 🚨 SECURITY BULLETIN")
        st.warning("""
        **⚠️ PHISHING SCAM ALERT:**
        Be cautious of SMS/WhatsApp messages offering unauthorized cash prizes or posing as bank verification. Do not share your banking OTP or CNIC.
        """)
        st.info("""
        **💡 RECOVERY STEP:**
        If your WhatsApp account has been hacked, delete the app, reinstall it, and register your number again to terminate active sessions.
        """)

# ── Main Controller ───────────────────────────────────────────────────────────
def main():
    initialize_session()
    load_css()

    # Premium top banner
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ CYBER CRIME CITIZEN PORTAL</h1>
        <p>National Cyber Investigation Agency - Government of Pakistan</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar Navigation ──
    with st.sidebar:
        st.markdown("### 🗺️ PORTAL NAVIGATION")
        
        pages = {
            "🏠 Portal Home": "home",
            "📋 File Cyber Complaint": "report_form",
            "📍 Track Case Status": "tracking",
            "📚 PECA 2016 Law Guide": "law_guide",
            "❓ Help & Victim Support": "help_support",
            "👮 Officer Command Center": "officer_terminal"
        }
        
        page_labels = list(pages.keys())
        page_values = list(pages.values())
        
        try:
            current_idx = page_values.index(st.session_state.current_page)
        except ValueError:
            current_idx = 0
            
        radio_key = f"nav_radio_{st.session_state.current_page}"
        selected_label = st.radio("Select Portal Area:", page_labels, index=current_idx, key=radio_key)
        selected_page = pages[selected_label]
        
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); padding: 1rem; border-radius: 8px; font-size: 0.85rem; color: #94a3b8; text-align: center;">
            <p style="margin: 0; font-weight: bold; color: #fff;">🔒 CITIZEN DATA PROTECTION</p>
            <p style="margin: 5px 0 0 0; line-height:1.4;">All reports and uploads are secured by military-grade end-to-end encryption protocols.</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Page Routing ──
    current = st.session_state.current_page
    
    if current == "home":
        render_hero_home()
    elif current == "report_form":
        from views.report_form import render_report_form
        render_report_form(set_page_config=False)
    elif current == "tracking":
        from views.tracking import render_tracking_page
        render_tracking_page(set_page_config=False)
    elif current == "law_guide":
        from views.law_guide import render_law_guide_page
        render_law_guide_page()
    elif current == "help_support":
        from views.help import render_help_page
        render_help_page()
    elif current == "officer_terminal":
        # ── Officer Portal Security Gate ──
        if 'officer_logged_in' not in st.session_state:
            st.session_state.officer_logged_in = False
            
        if not st.session_state.officer_logged_in:
            from views.officer_login import render_officer_login
            render_officer_login(set_page_config=False)
        else:
            from views.officer_panel import render_officer_panel
            render_officer_panel(set_page_config=False)

    # ── Chatbot Overlay ──
    from components.chatbot import render_chatbot
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("🤖 SECURE AI LEGAL ASSISTANT (CHAT)", expanded=False):
        render_chatbot()

    st.markdown(f"""<div class="footer"><p>© {datetime.now().year} NCIA Cyber Crime Division - Government of Pakistan</p></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
