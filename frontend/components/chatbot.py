"""
Cybercrime Assistant - AI Chatbot Component
Uses Groq API for intelligent legal and procedural guidance.
"""

import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def render_chatbot():
    """Renders a floating-style AI assistant."""
    st.markdown("---")
    st.subheader("🤖 CYBER ASSISTANT (AI)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about cyber laws, reporting process, or security tips..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                
                system_prompt = """
                You are a Cybercrime Legal Assistant for the Pakistan Cyber Crime Reporting System. 
                Your goal is to help users understand:
                1. How to report a crime.
                2. What falls under PECA 2016 (Prevention of Electronic Crimes Act).
                3. Digital security best practices (MFA, phishing awareness).
                4. The status of their reports (generally).
                
                Be professional, concise, and helpful. Do not provide legal advice that overrides official law, but guide them to the right sections.
                """
                
                response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                
                full_response = response.choices[0].message.content
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Assistant Offline: {str(e)}")
                st.info("Ensure GROQ_API_KEY is configured in your environment.")
