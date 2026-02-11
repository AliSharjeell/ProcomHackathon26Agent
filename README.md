# LangGraph RAG MCP Agent

A FastAPI-based intelligent agent that routes user queries to either a Retrieval-Augmented Generation (RAG) system for static information or a Model Context Protocol (MCP) client for dynamic tool execution and actions.

## Overview

This project implements a routing agent using LangGraph. It intelligently classifies user intent and directs requests to the appropriate handler:
- **RAG Node**: Handles questions about policies, fees, and static documentation by retrieving relevant context from a PDF.
- **MCP Node**: Handles action-oriented requests (e.g., checking balances, transfers) by interacting with an external MCP server.

## Architecture

The system is built on a modular architecture orchestrating three main components:

1.  **FastAPI Entry Point**: Receives HTTP requests (`/chat`) and initializes the LangGraph workflow.
2.  **LangGraph Controller**: Manages the state and flow of the conversation. It starts with a **Classifier Node** that uses an LLM to determine intent:
    *   **Retrieval (RAG)**: If the query is about static knowledge (policies, fees), it routes to the **RAG Node**. This node retrieves relevant chunks from a vector database (ChromaDB) populated from a PDF document and answers using the LLM.
    *   **Action (MCP)**: If the query implies an action or dynamic data access (checking balance), it routes to the **MCP Node**. This node connects to an external MCP server process via standard input/output (stdio) to execute tools.
3.  **MCP Client**: A standardized client that communicates with any MCP-compliant server, allowing the agent to extend its capabilities dynamically.

## Prerequisites

- Python 3.10+
- Ollama (running locally for embeddings) with `nomic-embed-text` model.
- An MCP Server (e.g., a banking server or brave search server) to connect to.
- OpenRouter API Key (for the LLM).
- `uv` (for running the MCP server).

## Installation

1. Clone the repository.
2. Create a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```ini
OPENROUTER_API_KEY=your_openrouter_key
PDF_FILE_PATH=path/to/your/document.pdf
OLLAMA_BASE_URL=http://localhost:11434
MCP_SERVER_COMMAND=uv
MCP_SERVER_ARGS=["run", "/ProcomBackendMCP/server.py"]
```

## Model Information

The agent is configured to use the `openrouter/aurora-alpha` model via OpenRouter. Ensure your API key has access to this model.

## Usage

1. **Start the Server**:

   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   
   ```bash
   uvicorn main:app --reload
   ```

2. **API Endpoint**:

   POST `/chat`
   
   Payload:
   ```json
   {
     "question": "What are the credit card fees?",
     "thread_id": "user_session_1"
   }
   ```

## Project Structure

- `main.py`: Application entry point and lifecycle management.
- `graph.py`: Defines the agent workflow (StateGraph).
- `rag.py`: Handles document ingestion and retrieval.
- `mcp_client.py`: Generic client for Model Context Protocol.
