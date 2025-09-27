import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class LegalCaseSearcher:
    def __init__(self):
        self.model = None
        self.index = None
        self.id2name = None
        self.store_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_store")
        self._load_index()
    
    def _load_index(self):
        """Load the FAISS index and metadata."""
        try:
            # Load the sentence transformer model
            self.model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
            
            # Load FAISS index
            index_path = os.path.join(self.store_dir, "legal_cases.index")
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"FAISS index not found at {index_path}. Please generate embeddings first.")
            
            self.index = faiss.read_index(index_path)
            
            # Load file name mapping
            id2name_path = os.path.join(self.store_dir, "id2name.json")
            if not os.path.exists(id2name_path):
                raise FileNotFoundError(f"ID to name mapping not found at {id2name_path}. Please generate embeddings first.")
            
            with open(id2name_path, "r") as f:
                self.id2name = json.load(f)
            
            print(f"✅ Loaded FAISS index with {len(self.id2name)} documents.")
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            raise
    
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
