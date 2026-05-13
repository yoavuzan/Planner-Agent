from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):

    messages: Annotated[list, add_messages]

    plan: list[str]

    current_task: str

    completed_tasks: list[str]