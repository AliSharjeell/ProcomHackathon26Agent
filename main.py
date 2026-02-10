import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from langchain_core.messages import HumanMessage

from rag import ingest_pdf
from graph import app_graph
from logger import log_interaction

# Pydantic Models
class ChatRequest(BaseModel):
    question: str
    thread_id: str = "default_thread"

class ChatResponse(BaseModel):
    answer: str
    classification: str

# Lifecycle Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    try:
        ingest_pdf()
    except Exception as e:
        print(f"Error during PDF ingestion: {e}")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(title="LangGraph RAG MCP Agent", lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Prepare input for LangGraph
        initial_state = {
            "messages": [HumanMessage(content=request.question)],
            "context": "",
            "classification": ""
        }
        
        # Run graph
        config = {"configurable": {"thread_id": request.thread_id}}
        result = await app_graph.ainvoke(initial_state, config=config)
        
        # Extract response
        messages = result["messages"]
        last_message = messages[-1]
        classification = result.get("classification", "unknown")
        
        # Log interaction
        log_interaction(request.thread_id, request.question, last_message.content)
        
        return ChatResponse(
            answer=last_message.content,
            classification=classification
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
