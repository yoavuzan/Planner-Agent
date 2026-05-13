import os
import sys

# Add the current directory to sys.path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.graph import create_graph
from app.config import get_models
from app.ui import print_output, visualize_graph, handle_interrupt, console
from rich.panel import Panel

def main():
    # 1. Configuration & Model Setup
    planner_model, executor_model, tools_dict = get_models()
    
    # 2. Graph Initialization
    checkpointer = MemorySaver()
    compiled_graph = create_graph(planner_model, executor_model, tools_dict, checkpointer=checkpointer)
    visualize_graph(compiled_graph)

    # 3. User Input
    console.print(Panel("[bold magenta]Planner Agent with Ollama[/bold magenta]", border_style="magenta"))
    user_input = console.input("\n[bold cyan]What would you like me to do? [/bold cyan]")
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "plan": [],
        "completed_tasks": []
    }
    config = {"configurable": {"thread_id": "1"}}

    # 4. Execution Loop
    console.print("\n[italic]Starting execution...[/italic]")
    for output in compiled_graph.stream(initial_state, config=config):
        print_output(output)

    # 5. Interrupt/Resume Loop
    while True:
        decision = handle_interrupt(compiled_graph, config)
        
        if decision is False: # No more steps
            break
        
        if decision: # Resuming from interrupt
            for output in compiled_graph.stream(Command(resume=decision), config=config):
                print_output(output)
        else: # Suspended but not at human_review (shouldn't happen with current graph but good for safety)
            for output in compiled_graph.stream(None, config=config):
                print_output(output)

    print("\nAll tasks completed!")

if __name__ == "__main__":
    main()
