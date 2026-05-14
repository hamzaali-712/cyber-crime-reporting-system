"""
Cybercrime Assistant - AI Chatbot Component
"""

import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def render_chatbot():
    """Renders a chat interface using the Groq API."""
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
                # Clean initialization to avoid 'proxies' error
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    st.error("API Key missing.")
                    return

                client = Groq(api_key=api_key)
                
                system_prompt = "You are a professional Cybercrime Assistant for the Pakistan NCIA. Provide clear guidance on laws (PECA 2016) and reporting procedures."
                
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    max_tokens=512
                )
                
                msg = response.choices[0].message.content
                st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
                
            except Exception as e:
                st.error(f"Chatbot Error: {str(e)}")
                st.info("Check your API key and connection.")
