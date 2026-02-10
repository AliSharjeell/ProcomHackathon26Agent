import requests
import time

BASE_URL = "http://localhost:8123"

def test_chat():
    print(f"Testing Chat Endpoint at {BASE_URL}...")
    # Give server time to start
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/docs")
            print("Server is up!")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            print(f"Waiting for server... {i+1}")
    else:
        print("Server failed to start.")
        return

    payload = {
        "question": "What is the fee for PayPak Classic card?",
        "thread_id": "test_verification"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"RAG Response: {data}")
    except Exception as e:
        print(f"RAG Test Failed: {e}")

    payload_mcp = {
        "question": "List files in directory",
        "thread_id": "test_verification_mcp"
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload_mcp)
        response.raise_for_status()
        data = response.json()
        print(f"MCP Response: {data}")
    except Exception as e:
        print(f"MCP Test Failed: {e}")

if __name__ == "__main__":
    test_chat()
