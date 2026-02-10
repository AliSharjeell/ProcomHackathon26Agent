import os
from datetime import datetime

CHAT_HISTORY_DIR = "chat_history"

def log_interaction(thread_id: str, question: str, answer: str):
    """
    Logs the question and answer to a markdown file specific to the thread_id.
    """
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)

    file_path = os.path.join(CHAT_HISTORY_DIR, f"thread_{thread_id}.md")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"## Interaction at {timestamp}\n\n")
        f.write(f"**User**: {question}\n\n")
        f.write(f"**Assistant**: {answer}\n\n")
        f.write("---\n\n")
