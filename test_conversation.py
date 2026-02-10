import asyncio
from graph import app_graph
from langchain_core.messages import HumanMessage

async def main():
    print("Testing Conversation Flow...")
    
    # 1. Ask to login without credentials
    question = "Log me in."
    print(f"\nUser: {question}")
    
    inputs = {
        "messages": [HumanMessage(content=question)],
        "context": "",
        "classification": "" # will be set by classifier
    }
    
    try:
        config = {"configurable": {"thread_id": "test_conv_1"}}
        result = await app_graph.ainvoke(inputs, config=config)
        
        last_message = result["messages"][-1]
        print(f"Agent: {last_message.content}")
        
        # Check if it called a tool (it shouldn't have, result['messages'][-1] should be AIMessage without tool_calls usually, 
        # but if it did call a tool and we returned the output, it would be a ToolMessage generally, or AIMessage with tool output in content if we mapped it so.
        # Our mcp_node returns AIMessage with "Tool Output: ..." if a tool was called.
        
        if "Tool Output" in last_message.content:
            print("FAILED: Agent called a tool instead of asking for info.")
        else:
            print("PASSED: Agent responded with text (likely asking for info).")
            
    except Exception as e:
        print(f"Error executing graph: {e}")

if __name__ == "__main__":
    asyncio.run(main())
