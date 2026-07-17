# frontend/app.py
import sys
import os
import uuid
import streamlit as st
from langgraph.types import Command

# ── Path setup ───────────────────────────────────────────
# Ensures agent/ is importable when Streamlit is launched from backend/
# If you always run `cd backend && streamlit run ../frontend/app.py`, this is
# redundant but harmless — belt-and-suspenders for deployment environments.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from agent.graph import build_graph
from agent.graph_state import AgentState

# ── Graph (built once, cached across reruns) ─────────────
@st.cache_resource
def get_graph():
    return build_graph()

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Analytics Copilot",
    page_icon="📊",
    layout="centered",
)

st.title("📊 Analytics Copilot")
st.caption("Ask questions about your edtech platform data in plain English.")
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
    st.session_state.messages = []          # list of {role, content, data}
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None       # current graph thread
if "awaiting_clarification" not in st.session_state:
    st.session_state.awaiting_clarification = False

# ── Render conversation history ──────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("data"):
            st.dataframe(msg["data"])

# ── Input handling ───────────────────────────────────────
graph = get_graph()

if st.session_state.awaiting_clarification:
    user_input = st.chat_input("Your answer...")
else:
    user_input = st.chat_input("Ask a question about your data...")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            if st.session_state.awaiting_clarification:
                # Resume the paused graph with the user's clarification answer
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                result = graph.invoke(Command(resume=user_input), config=config)
                st.session_state.awaiting_clarification = False

            else:
                # Fresh question — new thread ID
                st.session_state.thread_id = str(uuid.uuid4())
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                result = graph.invoke(
                    AgentState(user_question=user_input, mode="A"),
                    config=config,
                )

            # ── Handle interrupt (clarification needed) ──
            if "__interrupt__" in result:
                interrupt_val = result["__interrupt__"][0].value
                st.markdown(interrupt_val)
                st.session_state.awaiting_clarification = True
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": interrupt_val,
                    "data": None,
                })

            # ── Handle final result ──────────────────────
            else:
                answer = result.get("final_answer", "No answer returned.")
                data = result.get("execution_result")

                # Only show dataframe for multi-row results
                show_data = data and len(data) > 1

                st.markdown(answer)
                if show_data:
                    st.dataframe(data)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "data": data if show_data else None,
                })

    st.rerun()