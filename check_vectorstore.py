import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHROMA_PATH = "chroma_db"

def check_store():
    print(f"Checking vector store at {CHROMA_PATH}...")
    if not os.path.exists(CHROMA_PATH):
        print("Chroma DB directory does not exist.")
        return

    try:
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=OLLAMA_BASE_URL
        )
        vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        
        # Chroma doesn't have a direct len() on the wrapper sometimes, using gets
        # vectorstore._collection.count() is a common way if using the chroma client underlying
        count = vectorstore._collection.count()
        print(f"Number of documents in vector store: {count}")
        
        if count > 0:
            print("Fetching a sample document...")
            results = vectorstore.similarity_search("fee", k=1)
            if results:
                print(f"Sample content: {results[0].page_content[:200]}...")
            else:
                print("Search returned no results despite having documents.")
                
    except Exception as e:
        print(f"Error checking vector store: {e}")

if __name__ == "__main__":
    check_store()
