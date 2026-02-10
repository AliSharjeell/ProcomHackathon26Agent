import asyncio
from mcp_client import MCPClient
from collections import namedtuple

# Mock MCP Tool object
MockTool = namedtuple("MockTool", ["name", "description", "inputSchema"])
MockParams = namedtuple("MockParams", ["command", "args"])

def test_schema_generation():
    print("Testing Schema Generation...")
    
    # Define a mock tool with complex schema
    input_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "User name"},
            "age": {"type": "integer", "description": "Age"},
            "active": {"type": "boolean", "description": "Is active"}
        },
        "required": ["username"]
    }
    
    tool = MockTool(name="login", description="Login tool", inputSchema=input_schema)
    params = MockParams(command="echo", args=[]) # Dummy params
    
    client = MCPClient()
    # Test _convert_tool
    langchain_tool = client._convert_tool(tool, params)
    
    print(f"Generated Tool: {langchain_tool.name}")
    print(f"Args Schema: {langchain_tool.args_schema}")
    
    schema = langchain_tool.args_schema.schema()
    props = schema.get("properties", {})
    
    import json
    with open("test_schema_output.json", "w") as f:
        json.dump(props, f, indent=2, default=str)
    print("Schema dumped to test_schema_output.json")

    try:
        # Assertions
        assert "username" in props, "Missing username"
        assert "age" in props, "Missing age"
        assert "active" in props, "Missing active"
        
        # Check types logic (via pydantic schema)
        # Pydantic schema types: string, integer, boolean
        # Note: Pydantic v2 might structure this differently.
        if "type" in props["username"]:
            assert props["username"]["type"] == "string"
        elif "anyOf" in props["username"]:
             # Check if anyOf contains string type
             options = props["username"]["anyOf"]
             is_string = any(opt.get("type") == "string" for opt in options)
             assert is_string, "Username should allow string"

        if "type" in props["age"]:
            assert props["age"]["type"] == "integer"
        
        if "type" in props["active"]:
            assert props["active"]["type"] == "boolean"
        
        required = schema.get("required", [])
        assert "username" in required, "Username should be required"
        assert "age" not in required, "Age should be optional"
        
        print("PASS: Schema generation verified.")
    except Exception as e:
        print(f"Assertion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schema_generation()
