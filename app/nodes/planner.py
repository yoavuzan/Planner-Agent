from langchain_core.messages import SystemMessage
from .utils import parse_llm_list

def planner_node(state, model):
    user_request = state["messages"][-1].content

    prompt = f"""
    Create a concise development plan for the following request.
    User request: {user_request}

    The plan should:
    1. Be brief and actionable (maximum 2-3 steps).
    2. Focus only on direct actions (creating files, writing code).
    3. If testing is required, specify a separate test file (e.g., "Create test_add.py").
    4. Avoid generic steps like "understand requirements" or "research syntax".

    FORMAT: You MUST return a Python-style list of strings.
    Example: ["Create add.py with add function", "Create test_add.py to test add function"]
    Do NOT include any other text or markdown.
    """

    response = model.invoke([
        SystemMessage(content=prompt)
    ])

    plan = parse_llm_list(response.content)

    return {
        "plan": plan,
        "completed_tasks": []
    }
