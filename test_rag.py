import asyncio
from graph import app_graph
from langchain_core.messages import HumanMessage

async def main():
    print("Testing RAG flow...")
    question = "what is the fee to open credit card?"
    inputs = {
        "messages": [HumanMessage(content=question)],
        "context": "",
        "classification": ""
    }
    
    try:
        config = {"configurable": {"thread_id": "test_rag_1"}}
        result = await app_graph.ainvoke(inputs, config=config)
        
        last_message = result["messages"][-1]
        print(f"Question: {question}")
        print(f"Answer: {last_message.content}")
        
    except Exception as e:
        print(f"Error executing graph: {e}")

if __name__ == "__main__":
    asyncio.run(main())
