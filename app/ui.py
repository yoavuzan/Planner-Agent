from IPython.display import Image, display
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint
import questionary

console = Console()

def print_output(output):
    for key, value in output.items():
        if "messages" in value:
            last_msg = value["messages"][-1]
            content = ""
            
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    content += f"[bold blue]Tool Call:[/bold blue] {tc['name']}({tc['args']})\n"
            
            if last_msg.content:
                content += last_msg.content
            
            console.print(Panel(
                Markdown(content) if last_msg.content else content,
                title=f"[bold green]Node: {key}[/bold green]",
                border_style="bright_blue",
                expand=False
            ))
            
        if "plan" in value and key == "planner":
            plan_str = "\n".join([f"{i+1}. {task}" for i, task in enumerate(value['plan'])])
            console.print(Panel(
                plan_str,
                title="[bold yellow]Initial Plan[/bold yellow]",
                border_style="yellow"
            ))
            
        if "completed_tasks" in value and key == "complete_task":
            completed_str = "\n".join([f"✓ {task}" for task in value['completed_tasks']])
            console.print(Panel(
                completed_str,
                title="[bold green]Completed Tasks[/bold green]",
                border_style="green"
            ))

def visualize_graph(compiled_graph):
    try:
        display(Image(compiled_graph.get_graph().draw_png()))
    except Exception:
        pass

def handle_interrupt(compiled_graph, config):
    state = compiled_graph.get_state(config)
    if not state.next:
        return False
    
    if state.next[0] == "human_review":
        console.print("\n[bold red]─[/bold red]" * 2)
        console.print("[bold red]HUMAN REVIEW REQUIRED[/bold red]", justify="center")
        console.print("[bold red]─[/bold red]" * 2)
        
        if state.tasks and state.tasks[0].interrupts:
            interrupt_info = state.tasks[0].interrupts[0].value
            
            console.print(f"\n[bold yellow]Task:[/bold yellow] {interrupt_info.get('task')}")
            console.print(Panel(
                Markdown(interrupt_info.get('result', '')),
                title="[bold cyan]Result to Review[/bold cyan]",
                border_style="cyan"
            ))
            
            options = interrupt_info.get('options', ['approve', 'retry', 'end'])
            
            user_decision = questionary.select(
                "What should I do?",
                choices=options,
                default="approve"
            ).ask()
            
            if user_decision == "retry":
                explanation = questionary.text(
                    "Explain what went wrong (optional):",
                    default=""
                ).ask()
                if explanation:
                    return f"retry: {explanation}"
            
            return user_decision.lower()
    return None
