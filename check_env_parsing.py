import os
from dotenv import load_dotenv
import json

load_dotenv()

raw_args = os.getenv("MCP_SERVER_ARGS", "")
print(f"Raw MCP_SERVER_ARGS: '{raw_args}'")

split_args = raw_args.split()
print(f"Split args: {split_args}")

try:
    json_args = json.loads(raw_args)
    print(f"JSON loaded args: {json_args}")
except Exception as e:
    print(f"JSON load failed: {e}")
