import asyncio
from mcp_client import MCPClient
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import Tool
from pydantic import BaseModel, Field

async def main():
    print("Reproducing MPC Tool Schema Issue...")
    
    client = MCPClient()
    tools = await client.get_tools()
    
    login_tool = next((t for t in tools if t.name == "login"), None)
    if not login_tool:
        print("Login tool not found.")
        return

    print(f"Tool Name: {login_tool.name}")
    print(f"Tool Args Schema: {login_tool.args_schema}")
    print(f"Tool Description: {login_tool.description}")
    
    # Simulate what happens when LLM calls it with structured args
    # LangChain's bind_tools will inspect args_schema. 
    # If args_schema is None or generic, it might default to expecting a single string.
    
    if login_tool.args_schema is None:
        print("FAIL: args_schema is None. This will cause '__arg1' errors with structured output.")
    else:
        print("PASS: args_schema is present.")
        print(login_tool.args_schema.schema())

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
