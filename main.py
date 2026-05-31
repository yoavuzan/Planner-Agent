import os
import sys
import subprocess
import questionary
import uuid

# Add the current directory to sys.path to allow importing 'app' and 'data'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from app.graph import create_graph
from app.config import get_models
from app.ui import print_output, visualize_graph, handle_interrupt, console
from data.crud import get_existing_threads, delete_thread, DB_PATH
from rich.panel import Panel

def run_cli():
    # 1. Configuration & Model Setup
    planner_model, executor_model, tools_dict = get_models()

    # 2. Thread Selection
    db_path = DB_PATH
    
    while True:
        existing_threads = get_existing_threads(db_path)
        
        choices = ["Start a new thread"]
        if existing_threads:
            choices.append("Resume an existing thread")
            choices.append("Delete a thread")
        
        choice = questionary.select(
            "Thread Management:",
            choices=choices
        ).ask()

        if choice == "Delete a thread":
            thread_to_delete = questionary.select(
                "Select a thread to delete:",
                choices=existing_threads
            ).ask()
            
            if thread_to_delete:
                confirm = questionary.confirm(f"Are you sure you want to delete thread '{thread_to_delete}'?").ask()
                if confirm:
                    if delete_thread(thread_to_delete, db_path):
                        console.print(f"[bold green]Thread '{thread_to_delete}' deleted successfully.[/bold green]")
                continue # Refresh the menu
        
        if choice == "Resume an existing thread":
            thread_id = questionary.select(
                "Select a thread to resume:",
                choices=existing_threads
            ).ask()
            break
        elif choice == "Start a new thread":
            # Default to a new unique ID or let user name it
            name_choice = questionary.text("Enter a name for the new thread (optional, press Enter for random ID):").ask()
            thread_id = name_choice if name_choice else str(uuid.uuid4())[:8]
            break
        else:
            return # Exit if somehow nothing selected

    # 3. Graph Initialization with Persistent Checkpointer
    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        compiled_graph = create_graph(planner_model, executor_model, tools_dict, checkpointer=checkpointer)
        visualize_graph(compiled_graph)

        # 4. Check if thread has history
        state = compiled_graph.get_state({"configurable": {"thread_id": thread_id}})
        
        if state.values:
            console.print(f"\n[bold green]Resuming thread: {thread_id}[/bold green]")
            user_input = console.input("\n[bold cyan]How should we continue? [/bold cyan]")
            initial_state = None # Let it resume from last state
            # If we provide input, we should probably use Command or just stream with input
            # For simplicity, if they provide input, we wrap it as a HumanMessage
            input_msg = HumanMessage(content=user_input)
        else:
            console.print(Panel(f"[bold magenta]Planner Agent CLI - New Thread: {thread_id}[/bold magenta]", border_style="magenta"))
            user_input = console.input("\n[bold cyan]What would you like me to do? [/bold cyan]")
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "plan": [],
                "completed_tasks": []
            }
            input_msg = None

        config = {"configurable": {"thread_id": thread_id}}

        # 5. Execution Loop
        console.print("\n[italic]Starting execution...[/italic]")
        
        # If it's a new thread or we are sending a new message to existing thread
        stream_input = initial_state if initial_state else {"messages": [input_msg]}
        
        for output in compiled_graph.stream(stream_input, config=config):
            print_output(output)

        # 6. Interrupt/Resume Loop
        while True:
            decision = handle_interrupt(compiled_graph, config)
            
            if decision is False: # No more steps
                break
            
            if decision: # Resuming from interrupt
                for output in compiled_graph.stream(Command(resume=decision), config=config):
                    print_output(output)
            else: # Suspended but not at human_review
                for output in compiled_graph.stream(None, config=config):
                    print_output(output)

    print("\nAll tasks completed!")

def run_gui():
    console.print("[bold yellow]Starting GUI...[/bold yellow]")
    # Get the directory where main.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(["streamlit", "run", os.path.join(current_dir, "app", "gui.py")], cwd=current_dir)

def main():
    choice = questionary.select(
        "Choose your interface:",
        choices=["CLI (Command Line)", "GUI (Browser-based)"],
        default="CLI (Command Line)"
    ).ask()

    if choice and "CLI" in choice:
        run_cli()
    elif choice:
        run_gui()

if __name__ == "__main__":
    main()
