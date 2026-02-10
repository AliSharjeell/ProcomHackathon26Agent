import os
import operator
from typing import Annotated, Sequence, TypedDict, Union, Literal

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from rag import get_retriever, ingest_pdf
from mcp_client import MCPClient

# Load Environment Variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Persistent MCP Client
shared_mcp_client = MCPClient()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    classification: str

# 1. Setup LLM (OpenRouter)
llm = ChatOpenAI(
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openrouter/aurora-alpha",
    temperature=0
)

# 2. Define Nodes

def classifier_node(state: AgentState):
    """
    Classifies the user input to determine if it should go to RAG or MCP.
    """
    last_message = state["messages"][-1]
    
    # Enhanced classification prompt
    prompt = ChatPromptTemplate.from_template(
        """You are a routing agent for a banking assistant. 
        Determine if the user's request requires:
        1. "rag": Retrieving specific static information, policies, fees, charges, or product details from the bank's "Schedule of Charges" or "Info Document". 
           Examples: "what is the fee for credit card?", "savings account charges", "minimum balance requirements", "cheque book issuance fee".
        2. "mcp": Performing an action or accessing dynamic user data via a tool. 
           Examples: "log me in", "register a new user", "check my balance", "transfer money", "list my accounts", "account registration".

        User Request: {question}

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
    print("--- RAG NODE START ---")
    try:
        last_message = state["messages"][-1]
        question = last_message.content
        
        # Retrieve
        from rag import async_retrieve
        docs = await async_retrieve(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Generate
        prompt = ChatPromptTemplate.from_template(
            """Answer the question based only on the following context:
            
            {context}
            
            Question: {question}
            """
        )
        chain = prompt | llm
        response = await chain.ainvoke({"context": context, "question": question})
        
        print("--- RAG NODE END ---")
        return {"messages": [response], "context": context}
    except Exception as e:
        print(f"Error in rag_node: {e}")
        return {"messages": [AIMessage(content=f"Error in RAG processing: {str(e)}")]}

async def mcp_node(state: AgentState):
    """
    Executes MCP tools in a loop until the LLM provides a final response.
    """
    print("--- MCP NODE START ---")
    try:
        # Use the shared client
        tools = await shared_mcp_client.get_tools()
        
        if not tools:
            print("No MCP tools found.")
            return {"messages": [AIMessage(content="No MCP tools available/connected.")]}

        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(tools)
        
        # Add system prompt to guide the model
        system_message = SystemMessage(content="""You are a helpful AI assistant. You have access to a set of tools.

        Rules:
        1. ALWAYS ask for clarification if the user has not provided all necessary details (like username or password).
        2. When you have all the details, use the relevant tool to execute the action.
        3. After the tool runs, you will receive the output. Use that output to answer the user politely.
        4. Do NOT make up or guess parameter values.""")
        
        new_messages = []
        current_history = list(state["messages"])
        
        while True:
            # Prepend system message to history for each call
            full_messages = [system_message] + current_history
            
            # Run LLM
            response = await llm_with_tools.ainvoke(full_messages)
            new_messages.append(response)
            current_history.append(response)
            
            # If the LLM doesn't want to call any tools, we are done
            if not response.tool_calls:
                break
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                print(f"Tool call: {tool_call['name']}")
                
                selected_tool = next((t for t in tools if t.name == tool_call["name"]), None)
                if selected_tool:
                    try:
                        # Execute
                        tool_result = await selected_tool.coroutine(**tool_call["args"])
                        print(f"Tool Result: {tool_result}")
                        
                        # Convert tool result to string (MCP content is usually a list)
                        if isinstance(tool_result, list):
                            content_str = "\n".join([str(c) for c in tool_result])
                        else:
                            content_str = str(tool_result)
                            
                        # Create Tool Message
                        tool_message = ToolMessage(
                            tool_call_id=tool_call["id"],
                            content=content_str
                        )
                    except Exception as te:
                        print(f"Tool execution error: {te}")
                        tool_message = ToolMessage(
                            tool_call_id=tool_call["id"],
                            content=f"Error executing tool: {str(te)}"
                        )
                else:
                    tool_message = ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error: Tool '{tool_call['name']}' not found."
                    )
                
                new_messages.append(tool_message)
                current_history.append(tool_message)
            
            # After appending tool results, the loop continues to let the LLM see the results and respond
        
        print("--- MCP NODE END ---")
        return {"messages": new_messages}
    except Exception as e:
        print(f"Error in mcp_node: {e}")
        import traceback
        traceback.print_exc()
        return {"messages": [AIMessage(content=f"Error in MCP processing: {str(e)}")]}

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
