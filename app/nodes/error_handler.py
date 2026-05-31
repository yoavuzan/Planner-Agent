from langchain_core.messages import SystemMessage, HumanMessage

def error_handler_node(state):
    """
    Analyzes the state to identify why an error occurred and 
    provides a helpful message for the human review step.
    """
    messages = state.get("messages", [])
    plan = state.get("plan", [])
    current_task = state.get("current_task", "Unknown Task")
    
    last_msg = messages[-1] if messages else None
    error_reason = "Unknown error"
    
    # 1. Identify the reason
    if not last_msg:
        error_reason = "No messages found in state."
    elif not hasattr(last_msg, "content") or (not last_msg.content and not getattr(last_msg, 'tool_calls', None)):
        error_reason = "The AI model returned an empty or invalid response."
    else:
        # Check if it's a "silent failure" (talking but not acting)
        action_keywords = ["create", "write", "test", "add", "implement", "save"]
        if any(k in current_task.lower() for k in action_keywords):
            if not getattr(last_msg, 'tool_calls', None):
                error_reason = f"The task requires an action (like creating a file), but the agent only provided text without calling any tools."

    # 2. Format a clear message for the user
    diagnostic_message = f"""
❌ **ERROR DETECTED IN TASK EXECUTION**

**Current Task:** {current_task}
**Reason:** {error_reason}

**What happened?**
The system detected that the agent failed to progress correctly on this step. 

**How to fix?**
- Choose **'retry'** and provide a specific instruction (e.g., "You must call write_file to create the script").
- Choose **'end'** if you want to stop and debug the configuration.
    """
    
    # We return a HumanMessage so the 'human_review' node displays it as the 'result'
    return {
        "messages": [HumanMessage(content=diagnostic_message)]
    }
