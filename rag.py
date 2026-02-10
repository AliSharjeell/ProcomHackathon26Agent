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

import shutil

def ingest_pdf(force: bool = False):
    """
    Ingests the PDF file specified in environment variables into ChromaDB.
    Checks if the vector store is already populated to avoid re-ingestion on restart.
    Set force=True to clear existing vector store and re-ingest.
    """
    if force and os.path.exists(CHROMA_PATH):
        print(f"Forcing re-ingestion. Clearing vector store at {CHROMA_PATH}...")
        try:
            shutil.rmtree(CHROMA_PATH)
        except Exception as e:
            print(f"Error clearing vector store: {e}")

    if not PDF_FILE_PATH or not os.path.exists(PDF_FILE_PATH):
        print(f"PDF file not found at {PDF_FILE_PATH}. Skipping ingestion.")
        return

    vectorstore = get_vectorstore()
    
    # Check if we already have documents (only if not forcing)
    if not force:
        try:
            count = vectorstore._collection.count()
            if count > 0:
                print(f"Vector store already exists with {count} documents. Skipping ingestion.")
                return
        except Exception as e:
            print(f"Error checking vector store count: {e}. Proceeding with ingestion.")

    print(f"Ingesting PDF: {PDF_FILE_PATH}...")
    loader = PyPDFLoader(PDF_FILE_PATH)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    vectorstore.add_documents(documents=splits)
    print("Ingestion complete.")

import asyncio

def get_retriever() -> VectorStoreRetriever:
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever()

async def async_retrieve(question: str):
    """
    Asynchronously retrieves documents using the vector store retriever.
    Runs the blocking `invoke` method in a separate thread.
    """
    retriever = get_retriever()
    return await asyncio.to_thread(retriever.invoke, question)
