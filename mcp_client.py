import os
import shutil
import asyncio
from typing import Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import studio_client
from langchain_core.tools import Tool

MCP_SERVER_COMMAND = os.getenv("MCP_SERVER_COMMAND", "npx")
MCP_SERVER_ARGS = os.getenv("MCP_SERVER_ARGS", "").split()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = None

    async def connect(self):
        """
        Connects to the MCP server via stdio.
        """
        # Ensure command exists
        if not shutil.which(MCP_SERVER_COMMAND):
            print(f"Command {MCP_SERVER_COMMAND} not found.")
            return

        server_params = StdioServerParameters(
            command=MCP_SERVER_COMMAND,
            args=MCP_SERVER_ARGS,
        )

        self.exit_stack = asyncio.ExitStack()
        # We need to maintain the context manager alive
        # This is a bit tricky in a synchronous-ish wrapper, but usually done via start/stop lifecycle
        # For simplicity in this script, we'll assume usage within an async context or persistent session
        
        # However, mcp python client relies on context managers. 
        # We will use the studio_client context manager manually.
        pass # Actual connection logic happens when retrieving tools or executing

    async def get_tools(self) -> List[Tool]:
        """
        Connects to the MCP server, lists tools, and returns them as LangChain Tools.
        """
        tools = []
        if not shutil.which(MCP_SERVER_COMMAND):
            return tools

        server_params = StdioServerParameters(
            command=MCP_SERVER_COMMAND,
            args=MCP_SERVER_ARGS,
        )
        
        async with studio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                mcp_tools = await session.list_tools()
                
                for tool in mcp_tools.tools:
                    # Create a cleanup wrapper for execution to re-connect for each call
                    # functionality in a persistent graph is complex with stdio unless process is kept alive.
                    # For this simple setup, we will create a Tool that re-connects on execution.
                    # This is inefficient but safe for stateless usage.
                    
                    def create_runner(tool_name: str):
                        async def runner(**kwargs):
                            async with studio_client(server_params) as (r, w):
                                async with ClientSession(r, w) as s:
                                    await s.initialize()
                                    result = await s.call_tool(tool_name, arguments=kwargs)
                                    return result.content
                        return runner
                    
                    langchain_tool = Tool(
                        name=tool.name,
                        description=tool.description or "",
                        func=None,
                        coroutine=create_runner(tool.name)
                    )
                    tools.append(langchain_tool)
        return tools
