from langchain_core.messages import SystemMessage, HumanMessage

def executor_node(state, model):
    current_task = state["plan"][0]
    messages = state["messages"]

    system_prompt = f"""
    You are an expert executor. Your current task is: {current_task}

    If you need to use tools, call them. 
    IMPORTANT: 
    1. When using 'write_file', the 'content' argument should be the RAW string content you want in the file, NOT a JSON object.
    2. Use RELATIVE paths only (e.g., 'fibo.py', not '/workspace/fibo.py'). The tools already operate within the 'workspace' directory.
    
    If you receive an error from a tool, analyze it and try to fix your request.
    If you have tool results, use them to complete the task.
    When the task is finished, provide a brief summary of what you did.
    """

    # Let's combine messages with a task-specific instruction
    response = model.invoke([
        SystemMessage(content=system_prompt)
    ] + messages)

    return {
        "messages": [response],
        "current_task": current_task
    }