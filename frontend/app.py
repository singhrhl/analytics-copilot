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