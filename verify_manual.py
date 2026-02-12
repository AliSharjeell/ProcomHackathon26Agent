import requests
import json
import sys

def test_query(question):
    url = "http://localhost:8001/chat"
    payload = {
        "question": question,
        "thread_id": "test_verification_simple"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    with open("verification_result.txt", "w") as f:
        f.write("--- RAG Test ---\n")
        rag_res = test_query("what are the fees for credit cards?")
        f.write(json.dumps(rag_res, indent=2))
        f.write("\n\n--- MCP Test ---\n")
        mcp_res = test_query("100 rupees and my pin is 1234")
        f.write(json.dumps(mcp_res, indent=2))
        print("Done.")
