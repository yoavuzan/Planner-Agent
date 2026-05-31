from langgraph.graph import StateGraph, END
from functools import partial
from .state import AgentState
from .nodes.planner import planner_node
from .nodes.executor import executor_node
from .nodes.actions import action_node
from .nodes.router import complete_task, human_review
from .nodes.error_handler import error_handler_node
from .edges import exists_action, should_continue, review_decision

def create_graph(planner_model, executor_model, tools, checkpointer=None):
    builder = StateGraph(AgentState)

    # 1. Register Nodes
    builder.add_node("planner", partial(planner_node, model=planner_model))
    builder.add_node("executor", partial(executor_node, model=executor_model))
    builder.add_node("action", partial(action_node, tools=tools))
    builder.add_node("human_review", human_review)
    builder.add_node("complete_task", complete_task)
    builder.add_node("error_handler", error_handler_node)

    # 2. Set Entry Point
    builder.set_entry_point("planner")

    # 3. Define Edges
    builder.add_edge("planner", "executor")

    builder.add_conditional_edges(
        "executor",
        exists_action,
        {
            "action": "action",
            "human_review": "human_review",
            "error": "error_handler"
        }
    )

    builder.add_edge("action", "executor")
    builder.add_edge("error_handler", "human_review")

    builder.add_conditional_edges(
        "human_review",
        review_decision,
        {
            "approve": "complete_task",
            "retry": "executor",
            "end": END
        }
    )

    builder.add_conditional_edges(
        "complete_task",
        should_continue,
        {
            "continue": "executor",
            "finish": END
        }
    )

    return builder.compile(checkpointer=checkpointer)
