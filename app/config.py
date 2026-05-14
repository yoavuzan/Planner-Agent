import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from app.tools.file_tools import write_file, read_file, list_files, search_replace, delete_file, rename_file

load_dotenv()

def get_models():
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Planner Model: phi3:mini
    planner_model = ChatOllama(
        model="phi3:mini",
        temperature=0,
        base_url=base_url
    )
    
    # Executor Model: qwen2.5:3b with tools
    tools_list = [write_file, read_file, list_files, search_replace, delete_file, rename_file]
    executor_model = ChatOllama(
        model="qwen2.5:3b",
        temperature=0,
        base_url=base_url
    ).bind_tools(tools_list)
    
    tools_dict = {tool.name: tool for tool in tools_list}
    
    return planner_model, executor_model, tools_dict
