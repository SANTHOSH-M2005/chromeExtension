import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_DIR = os.getenv("CHROMA_DB_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../chroma_db")))

_db_instance = None

def get_chroma_db():
    global _db_instance
    if _db_instance is None:
        if not os.path.exists(DB_DIR):
            return None # Database hasn't been built yet
            
        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        _db_instance = Chroma(persist_directory=DB_DIR, embedding_function=embedding_function)
    return _db_instance

def get_relevant_laws(query: str, k: int = 3) -> str:
    """
    Searches the Chroma vector database for legal text relevant to the query.
    Returns a formatted string of the retrieved chunks.
    """
    db = get_chroma_db()
    if db is None:
        return "No local knowledge base found. Please run the ingestion script."
        
    results = db.similarity_search(query, k=k)
    
    if not results:
        return "No relevant laws found in the knowledge base."
        
    formatted_results = []
    for doc in results:
        source = doc.metadata.get('source_file', 'Unknown Document')
        formatted_results.append(f"Source: {source}\nExcerpt: {doc.page_content}\n")
        
    return "\n---\n".join(formatted_results)
