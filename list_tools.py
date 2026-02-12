import asyncio
from mcp_client import MCPClient

async def list_tools():
    client = MCPClient()
    try:
        tools = await client.get_tools()
        print(f"Found {len(tools)} tools:")
        for t in tools:
            print(f"- {t.name}: {t.description}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_tools())
