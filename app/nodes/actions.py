from langchain_core.messages import ToolMessage

def action_node(state, tools):
    tool_calls = state["messages"][-1].tool_calls
    results = []

    for t in tool_calls:
        try:
            result = tools[t["name"]].invoke(t["args"])
            content = str(result)
        except Exception as e:
            content = f"Error executing tool '{t['name']}': {str(e)}\nPlease check your arguments and try again."

        results.append(
            ToolMessage(
                tool_call_id=t["id"],
                name=t["name"],
                content=content
            )
        )

    return {
        "messages": results
    }