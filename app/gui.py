import streamlit as st
import os
import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from app.graph import create_graph
from app.config import get_models
from data.crud import get_existing_threads, delete_thread, DB_PATH

st.set_page_config(page_title="Planner Agent GUI", page_icon="🤖", layout="wide")

# Sidebar for Thread Management
with st.sidebar:
    st.title("🧵 Thread Management")
    
    existing_threads = get_existing_threads(DB_PATH)
    
    # New Thread
    st.subheader("New Thread")
    new_thread_name = st.text_input("Thread Name (optional)", key="new_thread_input")
    if st.button("Start New Thread", use_container_width=True):
        thread_id = new_thread_name if new_thread_name else str(uuid.uuid4())[:8]
        st.session_state.current_thread_id = thread_id
        st.rerun()

    if existing_threads:
        st.divider()
        st.subheader("Resume Thread")
        
        current_id = st.session_state.get("current_thread_id", existing_threads[0] if existing_threads else "gui_thread")
        
        if current_id not in existing_threads:
            options = [current_id] + existing_threads
        else:
            options = existing_threads
            
        selected_thread = st.selectbox("Select Thread", options=options, index=options.index(current_id) if current_id in options else 0)
        
        if selected_thread != current_id:
            st.session_state.current_thread_id = selected_thread
            st.rerun()
            
        st.divider()
        st.subheader("Delete Thread")
        thread_to_delete = st.selectbox("Select to delete", options=existing_threads, key="delete_select")
        if st.button("Delete Selected Thread", type="secondary", use_container_width=True):
            if delete_thread(thread_to_delete, DB_PATH):
                st.success(f"Deleted {thread_to_delete}")
                if st.session_state.get("current_thread_id") == thread_to_delete:
                    st.session_state.current_thread_id = "gui_thread"
                st.rerun()

# Initialize models and graph
if "graph" not in st.session_state:
    planner_model, executor_model, tools_dict = get_models()
    st.session_state.saver_context = SqliteSaver.from_conn_string(DB_PATH)
    st.session_state.checkpointer = st.session_state.saver_context.__enter__()
    st.session_state.graph = create_graph(planner_model, executor_model, tools_dict, checkpointer=st.session_state.checkpointer)

if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = "gui_thread"

current_thread_id = st.session_state.current_thread_id
st.session_state.config = {"configurable": {"thread_id": current_thread_id}}

# Load history from graph state
state = st.session_state.graph.get_state(st.session_state.config)
st.session_state.messages = state.values.get("messages", []) if state.values else []

st.title("🤖 Planner Agent")
st.caption(f"Connected to thread: **{current_thread_id}**")
st.markdown("---")

# Chat container
chat_container = st.container()

# Display existing messages
with chat_container:
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)

# Input area
if user_input := st.chat_input("What would you like me to do?"):
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant"):
            with st.status("Thinking...", expanded=True) as status:
                if not st.session_state.messages:
                    input_data = {
                        "messages": [HumanMessage(content=user_input)],
                        "plan": [],
                        "completed_tasks": []
                    }
                else:
                    input_data = {"messages": [HumanMessage(content=user_input)]}
                
                for output in st.session_state.graph.stream(input_data, config=st.session_state.config):
                    for key, value in output.items():
                        st.write(f"**Node:** {key}")
                        if "messages" in value:
                            last_msg = value["messages"][-1]
                            if last_msg.content:
                                st.write(last_msg.content)
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                for tc in last_msg.tool_calls:
                                    st.info(f"Tool Call: {tc['name']}")
                        if "plan" in value and key == "planner":
                            st.warning(f"Plan: {value['plan']}")
                
                status.update(label="Complete!", state="complete", expanded=False)
                st.rerun()

# Human-in-the-loop handling
state = st.session_state.graph.get_state(st.session_state.config)
if state.next and state.next[0] == "human_review":
    st.divider()
    st.subheader("⚠️ Human Review Required")
    
    if state.tasks and state.tasks[0].interrupts:
        interrupt_info = state.tasks[0].interrupts[0].value
        st.write(f"**Current Task:** {interrupt_info.get('task')}")
        st.info(f"**Result:** {interrupt_info.get('result')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Approve", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    for output in st.session_state.graph.stream(Command(resume="approve"), config=st.session_state.config):
                        pass
                st.rerun()
        with col2:
            retry_feedback = st.text_input("Explain what went wrong (optional):", key="retry_feedback")
            if st.button("Retry", use_container_width=True):
                with st.spinner("Processing..."):
                    decision = f"retry: {retry_feedback}" if retry_feedback else "retry"
                    for output in st.session_state.graph.stream(Command(resume=decision), config=st.session_state.config):
                        pass
                st.rerun()
        with col3:
            if st.button("End Session", type="secondary", use_container_width=True):
                with st.spinner("Closing..."):
                    for output in st.session_state.graph.stream(Command(resume="end"), config=st.session_state.config):
                        pass
                st.rerun()
