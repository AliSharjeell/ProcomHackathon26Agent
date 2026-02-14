
import requests
import json
import os
import time

# Configuration
BASE_URL = "http://localhost:8001/chat"
OUTPUT_FILE = "ui_capabilities_log.json"
GALLERY_FILE = "ui_gallery.md"
THREAD_ID = "ui_test_session_" + str(int(time.time()))

# Test Prompts covering diverse UI scenarios
TEST_CASES = [
    {
        "id": "greeting",
        "prompt": "Hi, I need help with my banking.",
        "desc": "General Greeting (Text Bubble)"
    },
    {
        "id": "balance",
        "prompt": "What is my current balance?",
        "desc": "Simple Data Retrieval (Text Bubble or Info)"
    },
    {
        "id": "transfer_start",
        "prompt": "I want to transfer money.",
        "desc": "Missing Information (Composite Form)"
    },
    {
        "id": "transfer_preview",
        "prompt": "Transfer 5000 to Ali.",
        "desc": "Transfer Preview (Confirmation Card)"
    },
    {
        "id": "show_cards",
        "prompt": "Show me my cards.",
        "desc": "List Items (Selection List / Info Table)"
    },
    {
        "id": "freeze_card",
        "prompt": "Freeze my Visa card.",
        "desc": "Action Confirmation (Confirmation / Security)"
    },
    {
        "id": "bill_pay",
        "prompt": "Pay my K-Electric bill.",
        "desc": "Bill Payment Flow (Composite Form / Confirmation)"
    },
    {
        "id": "analytics",
        "prompt": "How much did I spend last month?",
        "desc": "Data Visualization (Info Table)"
    }
]

def run_tests():
    results = []
    
    print(f"Starting UI Capability Test on {BASE_URL}...")
    print(f"Session ID: {THREAD_ID}")
    
    for case in TEST_CASES:
        print(f"\nTesting: {case['desc']} ('{case['prompt']}')")
        
        try:
            payload = {
                "question": case['prompt'],
                "thread_id": THREAD_ID
            }
            response = requests.post(BASE_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                raw_answer = data.get("answer", "")
                
                # Try to parse the inner JSON from the answer string
                try:
                    parsed_answer = json.loads(raw_answer)
                    print("  ✅ Valid JSON Response")
                    visual_type = parsed_answer.get("visual", {}).get("type", "UNKNOWN")
                    print(f"  Visual Type: {visual_type}")
                except json.JSONDecodeError:
                    print("  ❌ Invalid JSON in Answer (Likely Plain Text)")
                    parsed_answer = {"raw_text": raw_answer}
                    visual_type = "PLAIN_TEXT"
                
                result_entry = {
                    "case_id": case["id"],
                    "description": case["desc"],
                    "prompt": case["prompt"],
                    "full_response": data,
                    "parsed_answer": parsed_answer,
                    "visual_type": visual_type
                }
                results.append(result_entry)
                
            else:
                print(f"  ❌ HTTP Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Request Failed: {e}")
            import traceback
            traceback.print_exc()
            
        # small delay to prevent rate limiting
        time.sleep(1)

    # Save Log
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved raw log to {OUTPUT_FILE}")
    
    # Generate Gallery
    generate_gallery(results)

def generate_gallery(results):
    md_content = "# UI Component Gallery\n\n"
    md_content += f"Generated on: {time.ctime()}\n\n"
    
    for res in results:
        md_content += f"## {res['description']}\n"
        md_content += f"**User:** `{res['prompt']}`\n\n"
        
        visual = res["parsed_answer"].get("visual", {})
        voice = res["parsed_answer"].get("voice", "No Voice")
        
        md_content += f"**Voice:** \"{voice}\"\n\n"
        
        if visual:
            md_content += f"### Visual: `{visual.get('type', 'N/A')}`\n"
            md_content += "```json\n"
            md_content += json.dumps(visual, indent=2, ensure_ascii=False)
            md_content += "\n```\n"
        else:
            md_content += "> No Visual Data\n"
            
        md_content += "\n---\n"
        
    with open(GALLERY_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved gallery to {GALLERY_FILE}")

if __name__ == "__main__":
    run_tests()
