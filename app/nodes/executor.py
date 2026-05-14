from langchain_core.messages import SystemMessage, HumanMessage

def executor_node(state, model):
    current_task = state["plan"][0]
    completed_tasks = state.get("completed_tasks", [])
    messages = state["messages"]

    system_prompt = f"""
    You are an expert executor. 
    
    CURRENT TASK: {current_task}
    COMPLETED TASKS (IGNORE THESE): {completed_tasks}

    ALLOWED TOOLS: write_file, read_file, list_files, search_replace, delete_file, rename_file.
    
    STRICT RULES:
    1. FOCUS: Only perform actions required for the CURRENT TASK. Do not repeat work that was already done in COMPLETED TASKS.
    2. NO REPETITION: Do not call a tool to create or write a file if the history shows it was already successfully created for a previous task.
    3. ACTIONS REQUIRED: If the task says to "create", "write", "test", or "add", you MUST call a tool. 
    4. NO FAKING: Do not provide a summary claiming completion if you haven't called a tool for this specific task.
    5. TOOL USAGE: 
       - 'write_file' appends by default. Set 'append=False' to overwrite.
       - Use RELATIVE paths only.
    
    If you haven't performed the action for THIS task yet, CALL THE TOOL NOW.
    Only summarize once the tool confirms success for THIS CURRENT TASK.
    """

    # Let's combine messages with a task-specific instruction
    response = model.invoke([
        SystemMessage(content=system_prompt)
    ] + messages)

    return {
        "messages": [response],
        "current_task": current_task
    }