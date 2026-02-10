import os
import operator
from typing import Annotated, Sequence, TypedDict, Union, Literal

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from rag import get_retriever, ingest_pdf
from mcp_client import MCPClient

# Load Environment Variables for Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    classification: str

# 1. Setup LLM
llm = ChatGroq(
    temperature=0,
    model_name="llama3-70b-8192", 
    api_key=GROQ_API_KEY
)

# 2. Define Nodes

def classifier_node(state: AgentState):
    """
    Classifies the user input to determine if it should go to RAG or MCP.
    """
    last_message = state["messages"][-1]
    
    # Simple classification prompt
    prompt = ChatPromptTemplate.from_template(
        """You are a routing agent. Determine if the user's question requires retrieving information from a specific provided document (RAG) or using a general purpose tool (MCP) like checking filesystem, filesystem operations, or general knowledge.

        User Question: {question}

        Output ONLY "rag" or "mcp".
        """
    )
    chain = prompt | llm | StrOutputParser()
    classification = chain.invoke({"question": last_message.content}).strip().lower()
    
    # Fallback cleanup
    if "rag" in classification:
        classification = "rag"
    else:
        classification = "mcp"
        
    return {"classification": classification}

async def rag_node(state: AgentState):
    """
    Retrieves context and generates an answer.
    """
    last_message = state["messages"][-1]
    question = last_message.content
    
    # Retrieve
    retriever = get_retriever()
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Generate
    prompt = ChatPromptTemplate.from_template(
        """Answer the question based only on the following context:
        
        {context}
        
        Question: {question}
        """
    )
    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})
    
    return {"messages": [response], "context": context}

async def mcp_node(state: AgentState):
    """
    Executes MCP tools.
    """
    # For this simple example, we just pass to the LLM with tools bound.
    # In a real scenario, we'd bind the MCP tools to the LLM.
    
    mcp_client = MCPClient()
    tools = await mcp_client.get_tools()
    
    if not tools:
        return {"messages": [AIMessage(content="No MCP tools available/connected.")]}

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    last_message = state["messages"][-1]
    
    # We invoke the LLM with tools. 
    # NOTE: To actually execute the tool, we need a tool executing loop or pre-built agent.
    # For simplicity here, we will just simulate a single turn tool call or use LangChain's create_tool_calling_agent logic manually if needed.
    # But LangGraph recommends `prebuilt.ToolNode`.
    
    # Let's try to invoke and see if it calls a tool.
    response = llm_with_tools.invoke(state["messages"])
    
    # If the LLM wants to call a tool, we need to execute it.
    if response.tool_calls:
        # Execute first tool call for simplicity in this demo
        tool_call = response.tool_calls[0]
        selected_tool = next((t for t in tools if t.name == tool_call["name"]), None)
        if selected_tool:
            # Execute
            tool_result = await selected_tool.coroutine(**tool_call["args"])
            
            # Create Function/Tool Message
            # For simplicity, we just append the result as an AI message or similar, 
            # ideally we should follow tool message protocol.
            
            # Let's just return the tool result as the final answer for this simple pipeline
            return {"messages": [AIMessage(content=f"Tool Output: {tool_result}")]}
    
    return {"messages": [response]}

# 3. Define Graph

workflow = StateGraph(AgentState)

workflow.add_node("classifier", classifier_node)
workflow.add_node("rag", rag_node)
workflow.add_node("mcp", mcp_node)

workflow.add_edge(START, "classifier")

def route_decision(state: AgentState):
    return state["classification"]

workflow.add_conditional_edges(
    "classifier",
    route_decision,
    {
        "rag": "rag",
        "mcp": "mcp"
    }
)

workflow.add_edge("rag", END)
workflow.add_edge("mcp", END)

# 4. Setup Checkpointer
memory = MemorySaver()

# 5. Compile
app_graph = workflow.compile(checkpointer=memory)
