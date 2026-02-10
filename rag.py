import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

load_dotenv()

PDF_FILE_PATH = os.getenv("PDF_FILE_PATH")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHROMA_PATH = "chroma_db"

def get_vectorstore():
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=OLLAMA_BASE_URL
    )
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

def ingest_pdf():
    """
    Ingests the PDF file specified in environment variables into ChromaDB.
    Checks if the vector store is already populated to avoid re-ingestion on restart.
    """
    if not PDF_FILE_PATH or not os.path.exists(PDF_FILE_PATH):
        print(f"PDF file not found at {PDF_FILE_PATH}. Skipping ingestion.")
        return

    vectorstore = get_vectorstore()
    
    # Check if we already have documents (simple check)
    # Note: efficient check might depend on implementation, here we just check if dir exists and has content
    # But Chroma object is already created. Let's check collection count.
    # access underlying collection?
    # Simpler: If chroma_db folder exists and is not empty, assume ingested.
    # But allow force re-ingest? For now, simple check.
    
    if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
        print("Vector store already exists. Skipping ingestion.")
        return

    print("Ingesting PDF...")
    loader = PyPDFLoader(PDF_FILE_PATH)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    vectorstore.add_documents(documents=splits)
    print("Ingestion complete.")

def get_retriever() -> VectorStoreRetriever:
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever()
