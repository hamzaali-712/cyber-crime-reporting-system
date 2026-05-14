"""
Cybercrime Assistant - AI Chatbot Component
Direct API Implementation to bypass SDK proxy bugs.
"""

import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def render_chatbot():
    """Renders a chat interface using direct REST calls to Groq."""
    st.markdown("---")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about cyber laws or reporting..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    st.error("API Key missing.")
                    return

                # Direct API call to bypass Groq SDK / httpx proxy issues
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                system_prompt = "You are a professional Cybercrime Assistant for the Pakistan NCIA. Provide clear guidance on laws (PECA 2016) and reporting procedures."
                
                # Using the latest Llama 3.3 model for high performance
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    "temperature": 0.5,
                    "max_tokens": 1024
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    msg = data["choices"][0]["message"]["content"]
                    st.markdown(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                else:
                    # If 3.3 is too busy/heavy, fallback to 3.1 8b instant
                    st.warning("Switching to lightweight model...")
                    payload["model"] = "llama-3.1-8b-instant"
                    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        msg = data["choices"][0]["message"]["content"]
                        st.markdown(msg)
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                    else:
                        st.error(f"API Error ({response.status_code}): {response.text}")
                
            except Exception as e:
                st.error(f"System Error: {str(e)}")
