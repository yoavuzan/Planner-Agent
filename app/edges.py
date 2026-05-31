def exists_action(state):
    result = state["messages"][-1]
    
    # 1. Check for empty or invalid model responses
    if not hasattr(result, "content") or (not result.content and not result.tool_calls):
        return "error"

    # 2. Check for tool calls
    if len(result.tool_calls) > 0:
        return "action"
    
    # 3. Validation: If the task implies a tool action but none were used
    current_task = state["plan"][0].lower() if state.get("plan") else ""
    if not current_task:
        return "human_review" # Should go to should_continue and finish

    action_keywords = ["create", "write", "test", "add", "implement", "save", "delete", "rename", "fibo", "pow", "tic_tac_toe"]
    
    # Check if the last tool call in history was actually for this task
    # (Simple version: if task has keywords and last msg has no tool calls, it's suspicious)
    if any(k in current_task for k in action_keywords):
        # We'll allow it to go to human_review for now, but the crash is fixed.
        # If we wanted to force it, we'd return 'error'.
        return "human_review"
    
    return "human_review"

def should_continue(state):
    remaining = state["plan"]
    if not remaining:
        return "finish"
    return "continue"

def review_decision(state):
    last_msg = state["messages"][-1].content
    if "approve" in last_msg.lower():
        return "approve"
    elif "end" in last_msg.lower():
        return "end"
    return "retry"
