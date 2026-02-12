import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001/chat"

LOG_FILE = "demo_log.txt"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def send_message(question, thread_id):
    log(f"\n[User]: {question}")
    try:
        response = requests.post(BASE_URL, json={"question": question, "thread_id": thread_id})
        response.raise_for_status()
        data = response.json()
        log(f"[Agent]: {data['answer']}")
        return data['answer']
    except Exception as e:
        log(f"Error: {e}")
        return ""

def test_scene_1_bill_payment():
    log("\n--- Testing Scene 1: Bill Payment ---")
    thread_id = "demo_scene_1_full"
    send_message("Hey, did the K-Electric bill for Home arrive? I lost the paper.", thread_id)
    send_message("Yes, please pay it. My PIN is 1234.", thread_id)

def test_scene_2_netflix():
    log("\n--- Testing Scene 2: Netflix Trial ---")
    thread_id = "demo_scene_2_full"
    send_message("I want to get this Netflix free trial, but I don't trust them not to charge me later.", thread_id)
    send_message("Just 100 rupees. My PIN is 1234.", thread_id)

def test_scene_5_panic():
    log("\n--- Testing Scene 5: Panic Mode ---")
    thread_id = "demo_scene_5_full"
    send_message("I think my wallet was stolen! Lock everything!", thread_id)

def test_scene_6_account_freeze():
    log("\n--- Testing Scene 6: Account Freeze ---")
    thread_id = "demo_scene_6_full"
    send_message("Someone is trying to access my account! Freeze everything!", thread_id)
    # Don't actually freeze unless we can unfreeze easily. But let's verify intent.
    # The agent should ask for confirmation or PIN.
    # If the tool requires PIN in the prompt, let's provide it in the next turn if asked.

def wait_for_server():
    log("Waiting for server...")
    for i in range(10):
        try:
            requests.get("http://localhost:8001/docs")
            log("Server is ready.")
            return True
        except:
            time.sleep(2)
    log("Server failed to start.")
    return False

if __name__ == "__main__":
    # Clear log
    with open(LOG_FILE, "w") as f:
        f.write("Starting Demo Verification...\n")
        
    if wait_for_server():
        log("Verifying Demo Scenarios...")
        try:
            test_scene_1_bill_payment()
            test_scene_2_netflix()
            test_scene_5_panic() 
            test_scene_6_account_freeze()
        except Exception as e:
            log(f"Test failed: {e}")
