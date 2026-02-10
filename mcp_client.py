import os
import shutil
import asyncio
from typing import Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.tools import StructuredTool
from pydantic import create_model, Field
import json
import shlex

# Try to parse as JSON first (e.g. ["arg1", "arg 2"]), then fallback to shlex split
raw_args = os.getenv("MCP_SERVER_ARGS", "")
try:
    MCP_SERVER_ARGS = json.loads(raw_args)
    if not isinstance(MCP_SERVER_ARGS, list):
        MCP_SERVER_ARGS = [str(MCP_SERVER_ARGS)]
except json.JSONDecodeError:
    MCP_SERVER_ARGS = shlex.split(raw_args)

# Force python if not set, or use what's in env
MCP_SERVER_COMMAND = os.getenv("MCP_SERVER_COMMAND", "python")

class MCPClient:
    def __init__(self):
        pass

    async def get_tools(self) -> List[StructuredTool]:
        if not shutil.which(MCP_SERVER_COMMAND):
            return []

        server_params = StdioServerParameters(
            command=MCP_SERVER_COMMAND,
            args=MCP_SERVER_ARGS,
        )
        
        tools = []
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    mcp_tools = await session.list_tools()
                    
                    for tool in mcp_tools.tools:
                        tools.append(self._convert_tool(tool, server_params))
        except Exception as e:
            print(f"Error fetching tools: {e}")
            
        return tools

    def _convert_tool(self, tool, server_params) -> StructuredTool:
        def create_runner(tool_name: str):
            async def runner(**kwargs):
                async with stdio_client(server_params) as (r, w):
                    async with ClientSession(r, w) as s:
                        await s.initialize()
                        result = await s.call_tool(tool_name, arguments=kwargs)
                        return result.content
            return runner
        
        # Create Pydantic model from JSON schema
        fields = {}
        if tool.inputSchema and "properties" in tool.inputSchema:
            for prop_name, prop_def in tool.inputSchema["properties"].items():
                prop_type = str
                if prop_def.get("type") == "integer":
                    prop_type = int
                elif prop_def.get("type") == "number":
                    prop_type = float
                elif prop_def.get("type") == "boolean":
                    prop_type = bool
                elif prop_def.get("type") == "array":
                    prop_type = list
                elif prop_def.get("type") == "object":
                    prop_type = dict
                    
                if "required" in tool.inputSchema and prop_name in tool.inputSchema["required"]:
                    fields[prop_name] = (prop_type, Field(description=prop_def.get("description", "")))
                else:
                    fields[prop_name] = (Optional[prop_type], Field(default=None, description=prop_def.get("description", "")))
        
        if not fields:
            SchemaModel = create_model(f"{tool.name}Model")
        else:
            SchemaModel = create_model(f"{tool.name}Model", **fields)
        
        return StructuredTool(
            name=tool.name,
            description=tool.description or "",
            func=None,
            coroutine=create_runner(tool.name),
            args_schema=SchemaModel
        )
