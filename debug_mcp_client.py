import asyncio
import os
import shutil
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import json
import shlex

load_dotenv()

# Copy of arg parsing logic
raw_args = os.getenv("MCP_SERVER_ARGS", "")
try:
    MCP_SERVER_ARGS = json.loads(raw_args)
    if not isinstance(MCP_SERVER_ARGS, list):
        MCP_SERVER_ARGS = [str(MCP_SERVER_ARGS)]
except json.JSONDecodeError:
    MCP_SERVER_ARGS = shlex.split(raw_args)

MCP_SERVER_COMMAND = os.getenv("MCP_SERVER_COMMAND", "python")

async def main():
    print(f"Command: {MCP_SERVER_COMMAND}")
    print(f"Args: {MCP_SERVER_ARGS}")
    
    server_params = StdioServerParameters(
        command=MCP_SERVER_COMMAND,
        args=MCP_SERVER_ARGS,
    )
    
    print("Starting stdio client...")
    try:
        async with stdio_client(server_params) as (read, write):
            print("Stdio client started. Creating session...")
            async with ClientSession(read, write) as session:
                print("Session created. Initializing...")
                await session.initialize()
                print("Session initialized. Listing tools...")
                mcp_tools = await session.list_tools()
                print(f"Tools listed: {len(mcp_tools.tools)}")
                for tool in mcp_tools.tools:
                    print(f" - {tool.name}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
