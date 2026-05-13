import json
import re
from langchain_core.messages import SystemMessage

def planner_node(state, model):
    user_request = state["messages"][-1].content

    prompt = f"""
    Create a concise development plan for the following request.
    User request: {user_request}

    The plan should:
    1. Be brief and actionable (maximum 3-5 steps).
    2. Focus only on the direct actions needed (like creating files, writing code).
    3. Avoid generic steps like "understand requirements" or "research syntax".

    Return the plan as a Python list of strings.
    Example: ["Create script.py with hello world code", "Verify the file exists"]
    ONLY return the list, no other text.
    """

    response = model.invoke([
        SystemMessage(content=prompt)
    ])

    # Try to extract list using regex if eval fails or to be safe
    content = response.content.strip()
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        try:
            plan = eval(match.group(0))
        except:
            plan = [content] # Fallback
    else:
        plan = [content]

    return {
        "plan": plan,
        "completed_tasks": []
    }