from langgraph.types import interrupt
from langchain_core.messages import HumanMessage

def complete_task(state):
    plan = state["plan"]
    completed = state.get("completed_tasks", [])

    if plan:
        completed.append(plan[0])
        plan = plan[1:]

    return {
        "plan": plan,
        "completed_tasks": completed
    }

def human_review(state):
    # The graph will stop here and return this info to the user
    last_message = state["messages"][-1].content

    decision = interrupt({
        "task": state["current_task"],
        "result": last_message,
        "options": ["approve", "retry", "end"]
    })

    return {
        "messages": [HumanMessage(content=f"Human decision: {decision}")]
    }