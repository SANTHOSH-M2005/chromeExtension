import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DOCS_DIR = os.getenv("RAG_DOCS_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../rag/documents")))
DB_DIR = os.getenv("CHROMA_DB_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_db")))

def ingest_documents():
    print("Starting document ingestion...")
    
    # 1. Find all PDFs
    pdf_files = glob.glob(f"{DOCS_DIR}/**/*.pdf", recursive=True)
    if not pdf_files:
        print(f"No PDF files found in {DOCS_DIR}")
        return

    docs = []
    # 2. Load Documents
    for file_path in pdf_files:
        print(f"Loading {os.path.basename(file_path)}...")
        try:
            loader = PyPDFLoader(file_path)
            loaded_docs = loader.load()
            # Ensure metadata has the filename for citation
            for doc in loaded_docs:
                doc.metadata["source_file"] = os.path.basename(file_path)
            docs.extend(loaded_docs)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")

    print(f"Loaded {len(docs)} pages.")

    # 3. Chunking (Text Splitting)
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    # 4. Embeddings
    print("Initializing embedding model (this may take a moment to download on first run)...")
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Vector Database
    print("Saving to Chroma database...")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=DB_DIR
    )
    print(f"Successfully ingested {len(chunks)} chunks into {DB_DIR}!")

if __name__ == "__main__":
    ingest_documents()
