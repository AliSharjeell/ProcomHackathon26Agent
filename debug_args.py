import os
import json
import shlex
from dotenv import load_dotenv

load_dotenv()

raw_args = os.getenv("MCP_SERVER_ARGS", "")
print(f"Raw args: '{raw_args}'")

try:
    MCP_SERVER_ARGS = json.loads(raw_args)
    print(f"Parsed as JSON: {MCP_SERVER_ARGS}")
    if not isinstance(MCP_SERVER_ARGS, list):
        MCP_SERVER_ARGS = [str(MCP_SERVER_ARGS)]
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    MCP_SERVER_ARGS = shlex.split(raw_args)
    print(f"Parsed via shlex: {MCP_SERVER_ARGS}")

print(f"Final args list: {MCP_SERVER_ARGS}")
