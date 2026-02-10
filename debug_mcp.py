import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv
from mcp_client import MCPClient

load_dotenv()

async def main():
    print("Debugging MCP Client...")
    
    # Print environment to verify
    print(f"MCP_SERVER_COMMAND: {os.getenv('MCP_SERVER_COMMAND')}")
    print(f"MCP_SERVER_ARGS: {os.getenv('MCP_SERVER_ARGS')}")
    
    try:
        client = MCPClient()
        print("MCPClient initialized.")
        
        print("Attempting to get tools...")
        tools = await client.get_tools()
        print(f"Successfully retrieved {len(tools)} tools.")
        
        for tool in tools:
            print(f" - {tool.name}")
            
    except Exception as e:
        print("\n!!! CAUGHT EXCEPTION !!!")
        print(f"Type: {type(e)}")
        print(f"Error: {e}")
        
        if hasattr(e, 'exceptions'):
            print("Sub-exceptions:")
            for i, sub_exc in enumerate(e.exceptions):
                print(f"  [{i}] {type(sub_exc)}: {sub_exc}")
                traceback.print_exception(type(sub_exc), sub_exc, sub_exc.__traceback__)
        else:
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
