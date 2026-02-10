import asyncio
from graph import app_graph
from langchain_core.messages import HumanMessage

async def main():
    print("Testing Tool Evolution Loop (Full Flow)...")
    
    # 1. Ask to login with credentials
    question = "Log me in with username 'testuser3' and password 'TestPass123'."
    print(f"\nUser: {question}")
    
    inputs = {
        "messages": [HumanMessage(content=question)],
        "context": "",
        "classification": "" # will be set by classifier
    }
    
    try:
        config = {"configurable": {"thread_id": "test_loop_1"}}
        result = await app_graph.ainvoke(inputs, config=config)
        
        # In a loop, there might be multiple new messages
        # result["messages"] will have all messages for this turn
        for i, msg in enumerate(result["messages"]):
             print(f"Message {i} Type: {type(msg).__name__}")
             if hasattr(msg, "tool_calls") and msg.tool_calls:
                 print(f"  Tool Calls: {msg.tool_calls}")
             if hasattr(msg, "content"):
                 print(f"  Content: {msg.content}")

        last_message = result["messages"][-1]
        print(f"\nFinal Agent Output: {last_message.content}")
        
        # Verify it's an AIMessage and contains a natural confirmation
        if "Successfully" in last_message.content or "token" in last_message.content.lower():
            print("\nPASSED: Agent provided a natural language response after tool execution.")
        else:
            print("\nFAILED: Agent might have stopped early or returned raw tool output.")
            
    except Exception as e:
        print(f"Error executing graph: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
