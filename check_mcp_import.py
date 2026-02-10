try:
    from mcp.client.stdio import stdio_client
    print("Import successful: stdio_client found.")
except ImportError as e:
    print(f"Import failed: {e}")
    try:
        from mcp.client.stdio import studio_client
        print("Wait, studio_client found instead?")
    except ImportError:
        print("Neither found.")
        import mcp.client.stdio
        print(f"Available in mcp.client.stdio: {dir(mcp.client.stdio)}")
