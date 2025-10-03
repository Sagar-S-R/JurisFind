import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import tempfile
import sys

# Add helpers to path
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from helpers.azure_blob_helper import get_azure_blob_helper

class LegalCaseSearcher:
    def __init__(self):
        self.model = None
        self.index = None
        self.id2name = None
        self.temp_dir = tempfile.mkdtemp(prefix="faiss_data_")
        self._download_and_load_index()
    
    def _download_and_load_index(self):
        """Download FAISS index and metadata from Azure Blob Storage or load from local files."""
        try:
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            
            if connection_string:
                # Load from Azure Blob Storage
                self._load_from_azure(connection_string)
            else:
                # Fallback to local files for development
                print("⚠️  AZURE_STORAGE_CONNECTION_STRING not set, loading from local files...")
                self._load_from_local()
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            raise
    
    def _load_from_azure(self, connection_string):
        """Load index files from Azure Blob Storage using helper."""
        try:
            azure_helper = get_azure_blob_helper(connection_string)
            
            # Download FAISS index files
            print("📥 Downloading FAISS index from Azure Blob Storage...")
            faiss_files = azure_helper.download_faiss_index(self.temp_dir)
            
            if not faiss_files:
                raise Exception("Failed to download FAISS index from Azure Blob Storage")
            
            # Load the downloaded files
            self._load_model_and_index(faiss_files["index_path"], faiss_files["id2name_path"])
            print(f"✅ Loaded FAISS index with {len(self.id2name)} documents from Azure Blob Storage.")
            
        except Exception as e:
            print(f"❌ Error loading from Azure: {e}")
            raise
    
    def _load_from_local(self):
        """Load index files from local directories."""
        store_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faiss_store")
        
        index_path = os.path.join(store_dir, "legal_cases.index")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}. Please generate embeddings first.")
        
        id2name_path = os.path.join(store_dir, "id2name.json")
        if not os.path.exists(id2name_path):
            raise FileNotFoundError(f"ID to name mapping not found at {id2name_path}. Please generate embeddings first.")
        
        self._load_model_and_index(index_path, id2name_path)
        print(f"✅ Loaded FAISS index with {len(self.id2name)} documents from local files.")
    
    def _load_model_and_index(self, index_path, id2name_path):
        """Load the model, index, and mapping from file paths."""
        # Load the sentence transformer model
        print("🤖 Loading sentence transformer model...")
        self.model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        
        # Load FAISS index
        print("🔍 Loading FAISS index...")
        self.index = faiss.read_index(index_path)
        
        # Load file name mapping
        print("📋 Loading file name mapping...")
        with open(id2name_path, "r") as f:
            self.id2name = json.load(f)
    
    def search(self, query_text, top_k=5):
        """Search for similar legal cases based on query text."""
        if not self.model or not self.index or not self.id2name:
            raise RuntimeError("Search index not properly loaded. Please check if embeddings have been generated.")
        
        try:
            # Encode and normalize query
            query_vec = self.model.encode([query_text])
            query_vec = query_vec / np.linalg.norm(query_vec)
            
            # Search in FAISS index
            D, I = self.index.search(query_vec.astype('float32'), top_k)
            
            # Format results
            results = []
            for idx, score in zip(I[0], D[0]):
                if idx < len(self.id2name):  # Ensure valid index
                    results.append({
                        "filename": self.id2name[idx],
                        "score": float(score),
                        "similarity_percentage": round(float(score) * 100, 2)
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            raise
    
    def get_case_details(self, filename):
        """Get additional details about a specific case file."""
        # This can be extended to extract more metadata from the PDF
        pdf_path = os.path.join(os.path.dirname(__file__), "pdfs", filename)
        if os.path.exists(pdf_path):
            return {
                "filename": filename,
                "path": pdf_path,
                "size": os.path.getsize(pdf_path),
                "exists": True
            }
        else:
            return {
                "filename": filename,
                "exists": False
            }

# Global searcher instance
searcher = None

def get_searcher():
    """Get or create the global searcher instance."""
    global searcher
    if searcher is None:
        searcher = LegalCaseSearcher()
    return searcher
