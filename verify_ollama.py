import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import graph...")
    from graph import main_llm, classifier_llm
    
    print("Successfully imported graph.py")
    print(f"Main LLM Model: {main_llm.model}")
    print(f"Classifier LLM Model: {classifier_llm.model}")
    print(f"Main LLM Base URL: {main_llm.base_url}")
    
    # Optional: Try a simple invocation (might fail if Ollama is not running, but verifies code structure)
    # print("Attempting simple invocation...")
    # response = classifier_llm.invoke("Hello")
    # print(f"Response: {response.content}")
    
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
