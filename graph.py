import os
import operator
from typing import Annotated, Sequence, TypedDict, Union, Literal

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START

from rag import ingest_pdf
from mcp_client import MCPClient

# Load Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Persistent MCP Client
shared_mcp_client = MCPClient()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    classification: str
    tool_calls: list  # list of {name, args, result} dicts for frontend cards

# 1. Setup LLMs (Ollama)
# 1. Setup LLM (Groq via OpenAI compatible endpoint)
llm = ChatOpenAI(
    openai_api_key=GROQ_API_KEY,
    openai_api_base="https://api.groq.com/openai/v1",
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.6
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
            """You are a helpful and friendly banking assistant.
            
            OUTPUT FORMAT:
            You must output a VALID JSON object with the following structure:
            {{
                "voice": "The text to be spoken by the TTS engine (friendly and human-like).",
                "visual": {{
                    "type": "TEXT_BUBBLE",
                    "state": "display",
                    "data": {{
                        "markdown": "The markdown text to display on screen."
                    }}
                }}
            }}

            Answer the user's question based on the context provided below.
            
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
        system_message = SystemMessage(content="""You are a friendly and helpful banking assistant.
        
        OUTPUT FORMAT:
        You must output a VALID JSON object with the following structure:
        {
            "voice": "The text to be spoken by the TTS engine.",
            "visual": {
                "type": "WIDGET_TYPE",
                "state": "STATE",
                "data": { ... }
            }
        }
        
        WIDGET TYPES & DATA:
        - "COMPOSITE_FORM": When you need user input (e.g., amount, recipient). Data: {"title": "Title", "widgets": [{"id": "field_id", "type": "input_type", "label": "Label"}]}
        - "CONFIRMATION_CARD": Before executing a transfer or payment. Data: {"title": "Confirm", "fields": [{"label": "To", "value": "..."}, {"label": "Amount", "value": "..."}]}
        - "SELECTION_LIST": When offering choices (e.g., which card). Data: {"title": "Select", "items": [{"id": "item_id", "title": "Card ... (Include Last 4, Balance, Expiry etc.)"}]}
        - "INFO_TABLE": For lists of data (transactions, bills). Data: {"title": "History", "headers": [...], "rows": [[...]]}
        - "SECURITY_CHALLENGE": When you need a PIN. Data: {"method": "pin", "length": 4}
        - "TEXT_BUBBLE": Default for general conversation. Data: {"markdown": "..."}

        CRITICAL RULE — ALWAYS USE TOOLS FOR LIVE DATA:
        - "Show my cards" → get_cards → Visual: SELECTION_LIST (even if empty/error)
        - "Transfer money" → preview_transfer → Visual: CONFIRMATION_CARD
        - "Missing details" → Visual: COMPOSITE_FORM
        - "Authorize" → Visual: SECURITY_CHALLENGE
        
        HANDLING ERRORS & PARTIAL DATA:
        If a tool returns an error (e.g., "Connection Error"), you MUST still attempt to return the appropriate VISUAL structure if possible, or a "TEXT_BUBBLE" with a helpful message.
        HOWEVER, for "Show cards" or "List" requests, try to return an empty `SELECTION_LIST` or one with an error item so the UI stays consistent.

        General Rules:
        1. ALWAYS ask for clarification if details are missing.
        2. Use tools for real actions.
        3. Output JSON only. Do not wrap in markdown code blocks.
        4. CRITICAL: DO NOT rely on past conversation history for data. ALWAYS call the relevant tool again to get fresh data for every request.
        5. CRITICAL: NEVER invent or hallucinate data for function arguments. If the user has not provided specific details (like 'limit', 'pin', 'label', 'amount', 'recipient'), you MUST NOT call the tool. Instead, return a "COMPOSITE_FORM" or a question to get the missing details.
        6. For "create_virtual_card", "execute_transfer", "pay_bill", you MUST have explicit user confirmation and details.
        """)
        
        new_messages = []
        collected_tool_calls = []  # Collect for frontend
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
                        
                        # Convert tool result to string
                        # MCP returns list of TextContent objects — extract .text
                        if isinstance(tool_result, list):
                            parts = []
                            for c in tool_result:
                                if hasattr(c, 'text'):
                                    parts.append(c.text)
                                else:
                                    parts.append(str(c))
                            content_str = "\n".join(parts)
                        elif hasattr(tool_result, 'text'):
                            content_str = tool_result.text
                        else:
                            content_str = str(tool_result)
                            
                        # Create Tool Message
                        tool_message = ToolMessage(
                            tool_call_id=tool_call["id"],
                            content=content_str
                        )
                        
                        # Collect for frontend
                        try:
                            parsed = json.loads(content_str)
                        except Exception:
                            parsed = content_str
                        collected_tool_calls.append({
                            "name": tool_call["name"],
                            "args": tool_call["args"],
                            "result": parsed
                        })
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
        return {"messages": new_messages, "tool_calls": collected_tool_calls}
    except Exception as e:
        # Emergency handling for "tool_use_failed" where valid JSON was generated but rejected by strict tool binding
        error_str = str(e)
        if "failed_generation" in error_str:
            try:
                # Regex to find 'failed_generation': 'VALUE' at the end of the error dict
                import re
                # We look for the key, then a quote, then the content, then a matching closing quote, then closing braces
                # Using backreference \1 to match the same quote style (single or double)
                match = re.search(r"['\"]failed_generation['\"]\s*:\s*(['\"])(.*?)\1\s*}}", error_str, re.DOTALL)
                
                if match:
                    json_str_escaped = match.group(2)
                    # Manually unescape Python string representation to get actual JSON string
                    # 1. Replace \\n with \n
                    json_content = json_str_escaped.replace("\\n", "\n")
                    # 2. Replace \\' with ' (because it was inside single quotes)
                    json_content = json_content.replace("\\'", "'")
                    # 3. Replace \\" with " (if any)
                    json_content = json_content.replace('\\"', '"')
                    
                        # Log for debugging
                    with open("mcp_debug.log", "a") as f:
                        f.write(f"Extracted: {json_content}\n")

                    # 4. Handle trailing commas which break JSON parsing
                    json_content = json_content.strip()
                    if json_content.endswith(","):
                        json_content = json_content[:-1]

                    # Attempt to parse, improving robustness for truncated JSON
                    data = None
                    try:
                        data = json.loads(json_content)
                    except Exception:
                        # Attempt validation repair for truncated JSON
                        # We try appending various closing sequences
                        closing_sequences = ["}", "}}", "}}}", "]}", "]}}", "\"]}", "\"]}}", "\": null}}"]
                        for seq in closing_sequences:
                            try:
                                temp_content = json_content + seq
                                data = json.loads(temp_content)
                                # Successfully repaired
                                break
                            except Exception:
                                continue
                    
                    if data and ("visual" in data or "voice" in data):
                         # If we repaired it, use the repaired string
                         repaired_json_str = json.dumps(data) 
                         print(f"Recovered valid JSON from tool error via Regex: {repaired_json_str[:50]}...")
                         return {"messages": [AIMessage(content=repaired_json_str)]}
            except Exception as parse_error:
                with open("mcp_error.log", "a") as f:
                    f.write(f"Regex Recovery Failed: {parse_error}\nError Str Snippet: {error_str[-500:]}\n")
                print(f"Failed to recover JSON from error (Regex method): {parse_error}")

        with open("mcp_error.log", "a") as f:
            f.write(f"MCP Node Error: {e}\n")
            import traceback
            traceback.print_exc(file=f)
            
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

# Note: The app_graph compilation is now handled in main.py, so we only export 'workflow'.
