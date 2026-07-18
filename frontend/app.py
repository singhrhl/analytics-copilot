# frontend/app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

META_KEYWORDS = [
    "what is this", "what data", "what can you", "tell me about",
    "what columns", "what tables", "what metrics", "what does",
    "explain the", "describe the", "how does this work",
    "what are you", "who are you", "what is the dataset",
]

META_RESPONSE = (
    "I can only answer questions about the platform's usage data — "
    "things like DAU, MAU, retention, session goals, and user segments. "
    "Check the sidebar for example questions and what's available. "
    "I can't explain concepts or answer questions about the assistant itself."
)

def is_meta_question(question: str) -> bool:
    q = question.lower()
    return any(kw in q for kw in META_KEYWORDS)

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Analytics Copilot",
    page_icon="📊",
    layout="centered",
)

st.title("📊 Analytics Copilot")
st.caption("Ask questions about your edtech platform data in plain English.")

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("📋 About this Dataset")
    st.markdown("""
    **Platform:** Edtech learning platform (synthetic data)  
    **Period:** January – December 2025  
    **Scale:** 2,000 users · 15,000 sessions · 40,000 events

    **What you can ask about:**
    - 📈 Daily/Monthly Active Users (DAU, MAU)
    - 🔄 Retention (D1, D7, Curriculum)
    - 🎯 Session goals (deep study, revision, quick quiz)
    - 📚 Target exams (JEE, NEET, Boards)
    - 👤 User segments (grade, device, curriculum)

    **Example questions:**
    - *What's our DAU?*
    - *How many JEE students signed up in March?*
    - *What's our D7 retention?*
    - *How many deep study sessions happened last week?*

    ---
    ⚠️ This assistant answers questions using SQL against  
    structured data only. It cannot answer general knowledge  
    questions or explain concepts outside this dataset.
    """)

# ── Session state init ───────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "awaiting_clarification" not in st.session_state:
    st.session_state.awaiting_clarification = False

# ── Render conversation history ──────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("data"):
            st.dataframe(msg["data"])

# ── Input handling ───────────────────────────────────────
if st.session_state.awaiting_clarification:
    user_input = st.chat_input("Your answer...")
else:
    user_input = st.chat_input("Ask a question about your data...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Meta-question guard
    if not st.session_state.awaiting_clarification and is_meta_question(user_input):
        with st.chat_message("assistant"):
            st.markdown(META_RESPONSE)
        st.session_state.messages.append({
            "role": "assistant",
            "content": META_RESPONSE,
            "data": None,
        })
        st.rerun()

    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if st.session_state.awaiting_clarification:
                        resp = requests.post(
                            f"{BACKEND_URL}/clarify",
                            json={
                                "answer": user_input,
                                "thread_id": st.session_state.thread_id,
                            },
                            timeout=60,
                        )
                    else:
                        resp = requests.post(
                            f"{BACKEND_URL}/query",
                            json={"question": user_input, "mode": "A"},
                            timeout=60,
                        )

                    resp.raise_for_status()
                    result = resp.json()

                except requests.exceptions.Timeout:
                    st.error("Request timed out — the backend took too long to respond. Try again.")
                    st.stop()
                except requests.exceptions.RequestException as e:
                    st.error(f"Backend error: {e}")
                    st.stop()

                # Store thread_id from response
                st.session_state.thread_id = result.get("thread_id")

                if result["type"] == "clarification":
                    st.markdown(result["question"])
                    st.session_state.awaiting_clarification = True
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["question"],
                        "data": None,
                    })

                else:
                    answer = result.get("answer", "No answer returned.")
                    data = result.get("data")
                    show_data = data and len(data) > 1

                    st.markdown(answer)
                    if show_data:
                        st.dataframe(data)

                    st.session_state.awaiting_clarification = False
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "data": data if show_data else None,
                    })

        st.rerun()