import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(page_title="Chat", page_icon="💬")
st.title("বাংলা এইচএসসি ২৬ চ্যাটবট")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("আপনার প্রশ্ন লিখুন:")

if st.button("Send") and query.strip():
    response = requests.post(API_URL, json={"question": query})
    if response.status_code == 200:
        answer = response.json()["answer"]
        st.session_state.chat_history.append(("user", query))
        st.session_state.chat_history.append(("bot", answer))
    else:
        st.error("API error")

for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**{role}:** {text}")
    else:
        st.markdown(f"<div style='background:#f1f1f1;padding:10px;border-radius:5px'><b>{role}:</b> {text}</div>", unsafe_allow_html=True)
