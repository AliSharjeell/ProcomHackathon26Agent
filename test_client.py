import os
import requests
import json

BASE_URL = "http://localhost:8000"

def test_rag_flow():
    print("\n--- Testing RAG Flow ---")
    payload = {
        "question": "What is the fee for PayPak Classic card?",
        "thread_id": "test_thread_rag"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Question: {payload['question']}")
        print(f"Answer: {data.get('answer')}")
        print(f"Classification: {data.get('classification')}")
        
        if data.get('classification') == 'rag':
            print("SUCCESS: Correctly classified as RAG.")
        else:
            print(f"WARNING: Classified as {data.get('classification')}, expected 'rag'.")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def test_mcp_flow():
    print("\n--- Testing MCP Flow (General Knowledge/System) ---")
    payload = {
        "question": "List files in the current directory", 
        "thread_id": "test_thread_mcp"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Question: {payload['question']}")
        print(f"Answer: {data.get('answer')}") # Might be tool output or LLM interpretation
        print(f"Classification: {data.get('classification')}")
        
        if data.get('classification') == 'mcp':
            print("SUCCESS: Correctly classified as MCP.")
        else:
            print(f"WARNING: Classified as {data.get('classification')}, expected 'mcp'.")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print(f"Testing API at {BASE_URL}")
    test_rag_flow()
    test_mcp_flow()
