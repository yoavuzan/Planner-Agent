def exists_action(state):
    result = state["messages"][-1]
    if len(result.tool_calls) > 0:
        return "action"
    
    # If no tool calls, check if the agent is claiming to be done 
    # when the task clearly requires an action (like "create", "write", "test")
    current_task = state["plan"][0].lower()
    action_keywords = ["create", "write", "test", "add", "implement", "save", "delete", "rename"]
    
    if any(k in current_task for k in action_keywords):
        # The agent might be hallucinating completion. 
        # We can check if it actually performed any actions in the previous messages
        # for this specific task, but a simpler check is usually enough.
        return "human_review"
    
    return "human_review"

def should_continue(state):
    remaining = state["plan"]
    if len(remaining) == 0:
        return "finish"
    return "continue"

def review_decision(state):
    last_msg = state["messages"][-1].content
    if "approve" in last_msg.lower():
        return "approve"
    elif "end" in last_msg.lower():
        return "end"
    return "retry"
