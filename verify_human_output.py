import requests
import json
import time

def test_query(question):
    url = "http://localhost:8001/chat"
    payload = {
        "question": question,
        "thread_id": "test_verification_001"
    }
    
    try:
        print(f"Sending query: {question}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("\n--- Response ---")
        print(f"Answer: {data['answer']}")
        print(f"Classification: {data['classification']}")
        print("----------------\n")
        return data
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running?")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    # Simple check loop
    max_retries = 5
    for i in range(max_retries):
        try:
            requests.get("http://localhost:8001/docs")
            print("Server is ready.")
            break
        except:
            time.sleep(2)
            print(f"Waiting... ({i+1}/{max_retries})")
    
    # Test RAG
    print("\nTesting RAG Response (should be friendly):")
    test_query("what are the fees for credit cards?")
    
    # Test MCP (Mocking a tool call scenario might be hard without valid creds, 
    # but the prompt should catch generic interactions)
    print("\nTesting MCP Response (should be friendly):")
    test_query("100 rupees and my pin is 1234")
