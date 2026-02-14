
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"API Key found: {bool(api_key)}")

llm = ChatOpenAI(
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="openai/gpt-oss-20b:free",
    temperature=0
)

try:
    print("Invoking LLM...")
    response = llm.invoke("Hello")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
