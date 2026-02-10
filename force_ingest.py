from rag import ingest_pdf
import os

if __name__ == "__main__":
    print("Forcing PDF ingestion...")
    ingest_pdf()
    print("Ingestion returned.")
