import re
import ast

def parse_llm_list(content: str) -> list[str]:
    """Robustly parse a Python-like list from LLM output."""
    # 1. Clean up markdown code blocks
    content = re.sub(r'```python|```json|```', '', content).strip()
    
    # 2. Try to find anything between the first [ and the last ]
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        list_str = match.group(0)
        try:
            # Safely evaluate the string as a Python literal
            parsed = ast.literal_eval(list_str)
            if isinstance(parsed, list):
                # Ensure all elements are strings and not nested lists
                return [str(item).strip() for item in parsed if item]
        except Exception:
            # If ast.literal_eval fails, try manual line-by-line cleanup
            pass

    # 3. Fallback: Split by lines and look for common list indicators
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove list markers like "1. ", "- ", "* ", '"', "'" and commas
        # Also handle cases where a line might start with a quote and end with a quote/comma
        cleaned = re.sub(r'^(\d+\.|\-|\*)\s*', '', line.strip())
        cleaned = cleaned.strip('[],"\' ')
        
        # If the line was originally like: "Task 1", "Task 2"
        # and it got split incorrectly or has trailing characters:
        if cleaned.endswith('",'): cleaned = cleaned[:-2]
        if cleaned.endswith("',"): cleaned = cleaned[:-2]
        
        if cleaned:
            cleaned_lines.append(cleaned.strip())
            
    return cleaned_lines if cleaned_lines else [content]
