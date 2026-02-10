try:
    import fastapi
    import uvicorn
    import langgraph
    import langchain
    import langchain_groq
    import langchain_community
    import langchain_chroma
    import pypdf
    import dotenv
    import mcp
    import chromadb
    print("All dependencies imported successfully.")
except ImportError as e:
    print(f"Import Error: {e}")
