import os
import sys
from rag import ingest_pdf

if __name__ == "__main__":
    print("Starting forced re-ingestion process...")
    try:
        ingest_pdf(force=True)
        print("Forced re-ingestion successful.")
    except Exception as e:
        print(f"Forced re-ingestion failed: {e}")
        import traceback
        traceback.print_exc()
