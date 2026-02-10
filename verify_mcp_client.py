import asyncio
import os
from dotenv import load_dotenv
from mcp_client import MCPClient

load_dotenv()

async def main():
    print("Testing MCPClient...")
    try:
        client = MCPClient()
        print("MCPClient initialized.")
        
        # Check if we can get tools
        print("Attempting to get tools...")
        tools = await client.get_tools()
        print(f"Successfully retrieved {len(tools)} tools.")
        for tool in tools:
            print(f" - {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"Error during MCPClient verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
