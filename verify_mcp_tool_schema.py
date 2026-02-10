import asyncio
import sys
from mcp_client import MCPClient

async def main():
    print("Verifying MCP Tool Schema...")
    
    try:
        client = MCPClient()
        tools = await client.get_tools()
        
        login_tool = next((t for t in tools if t.name == "login"), None)
        if not login_tool:
            print("Login tool not found.")
            return

        print(f"Tool Name: {login_tool.name}")
        print(f"Tool Args Schema: {login_tool.args_schema}")
        
        if login_tool.args_schema:
            print("Schema Properties:")
            print(login_tool.args_schema.schema().get("properties"))
            
            props = login_tool.args_schema.schema().get("properties", {})
            if "username" in props and "password" in props:
                print("PASS: Schema contains expected fields.")
            else:
                print("FAIL: Schema missing expected fields.")
        else:
            print("FAIL: args_schema is still None.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
