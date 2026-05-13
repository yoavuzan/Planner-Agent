import os
import sys

# Add the current directory to sys.path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.graph import create_graph

def generate_graph_image():
    # We don't need real models just to draw the graph
    graph = create_graph(None, None, None)
    
    try:
        # Generate the PNG data
        png_data = graph.get_graph().draw_mermaid_png()
        
        with open("graph.png", "wb") as f:
            f.write(png_data)
        
        print("Successfully generated graph.png")
    except Exception as e:
        print(f"Could not generate PNG image: {e}")
        print("Falling back to Mermaid text representation:")
        print(graph.get_graph().draw_mermaid())

if __name__ == "__main__":
    generate_graph_image()
