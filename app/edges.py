def exists_action(state):
    result = state["messages"][-1]
    return len(result.tool_calls) > 0

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
