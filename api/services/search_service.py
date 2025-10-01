import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from azure.storage.blob import BlobServiceClient
import tempfile

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
        """Load index files from Azure Blob Storage."""
        container_name = os.getenv("AZURE_DATA_CONTAINER", "data")
        
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        # Download FAISS index
        index_path = os.path.join(self.temp_dir, "legal_cases.index")
        print("📥 Downloading FAISS index from Azure Blob Storage...")
        with open(index_path, "wb") as f:
            blob_client = container_client.get_blob_client("faiss_store/legal_cases.index")
            download_stream = blob_client.download_blob()
            f.write(download_stream.readall())
        
        # Download ID to name mapping
        id2name_path = os.path.join(self.temp_dir, "id2name.json")
        print("📥 Downloading ID mapping from Azure Blob Storage...")
        with open(id2name_path, "wb") as f:
            blob_client = container_client.get_blob_client("faiss_store/id2name.json")
            download_stream = blob_client.download_blob()
            f.write(download_stream.readall())
        
        self._load_model_and_index(index_path, id2name_path)
        print(f"✅ Loaded FAISS index with {len(self.id2name)} documents from Azure Blob Storage.")
    
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
