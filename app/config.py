import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from app.tools.file_tools import write_file, read_file, list_files, search_replace, delete_file, rename_file

load_dotenv()

def get_models():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    tools_list = [write_file, read_file, list_files, search_replace, delete_file, rename_file]
    tools_dict = {tool.name: tool for tool in tools_list}

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        planner_model = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=api_key
        )
        
        executor_model = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=api_key
        ).bind_tools(tools_list)
        
    else: # Default to Ollama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        planner_model_name = os.getenv("OLLAMA_PLANNER_MODEL", "phi3:mini")
        executor_model_name = os.getenv("OLLAMA_EXECUTOR_MODEL", "qwen2.5:3b")
        
        planner_model = ChatOllama(
            model=planner_model_name,
            temperature=0,
            base_url=base_url
        )
        
        executor_model = ChatOllama(
            model=executor_model_name,
            temperature=0,
            base_url=base_url
        ).bind_tools(tools_list)
    
    return planner_model, executor_model, tools_dict
