import asyncio
import sys
import json
from mcp_client import MCPClient

async def main():
    print("Debugging MCP Login Tool...")
    
    # Force Windows event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        client = MCPClient()
        # Connect explicitly or let get_tools handle it? 
        # mcp_client.py's get_tools connects, lists tools, and returns LangChain tools.
        # The LangChain tools have a coroutine that connects and calls the tool.
        
        print("Fetching tools...")
        tools = await client.get_tools()
        
        login_tool = next((t for t in tools if t.name == "login"), None)
        if not login_tool:
            print("Login tool not found.")
            return

        print(f"Found login tool. Args schema: {login_tool.args_schema.schema()}")
        
        # Test credentials from user request
        username = "testuser3" # Or "testuser"
        password = "TestPass123"
        
        print(f"Calling login with username={username}, password={password}")
        
        # Invoke the tool directly
        # The coroutine expects kwargs
        result = await login_tool.coroutine(username=username, password=password)
        
        print("\nTool Result:")
        print(result)
        
        # If result is keys/values string, parse it
        try:
             if isinstance(result, str):
                 print("\nParsed Result:")
                 print(json.loads(result))
             elif isinstance(result, list) and result and hasattr(result[0], 'text'):
                 print(f"\nText Content: {result[0].text}")
        except:
            pass

    except Exception as e:
        print(f"\nCaught unexpected exception in test script: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
