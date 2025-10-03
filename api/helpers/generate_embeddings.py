import fitz 
from tqdm import tqdm
import os
import sys
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# Add helpers to path
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from azure_blob_helper import get_azure_blob_helper, generate_and_upload_faiss_index

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        return " ".join(text.split())  
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ""

def generate_embeddings(pdf_dir_path=None, max_files=None, use_azure=False):
    """Generate embeddings for PDF files and save to FAISS index."""
    
    # Check if we should use Azure
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if use_azure and connection_string:
        print("🔄 Using Azure Blob Storage for embedding generation...")
        result = generate_and_upload_faiss_index(
            local_pdf_dir=pdf_dir_path, 
            connection_string=connection_string, 
            max_files=max_files
        )
        
        if result["success"]:
            print(f"✅ Azure embedding generation complete: {result['documents_processed']} documents processed")
        else:
            print(f"❌ Azure embedding generation failed: {result['error']}")
        
        return result
    
    # Use local file processing (existing logic)
    print("🔄 Using local file system for embedding generation...")
    
    # Set default PDF directory if not provided
    if pdf_dir_path is None:
        pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pdfs")
    else:
        pdf_dir = pdf_dir_path
    
    # Get PDF paths
    pdf_paths = sorted([
        os.path.join(pdf_dir, f)
        for f in os.listdir(pdf_dir)
        if f.lower().endswith(".pdf")
    ])

    print(f"Found {len(pdf_paths)} PDF files in {pdf_dir}")

    # Extract text from PDFs
    texts = []
    file_names = []

    # Process ALL files if max_files is None, otherwise limit
    files_to_process = pdf_paths if max_files is None else pdf_paths[:max_files]
    
    for path in tqdm(files_to_process, desc="Extracting text from PDFs"):
        text = extract_text_from_pdf(path)
        if text.strip():
            texts.append(text)
            file_names.append(os.path.basename(path))

    print(f"✅ Extracted text from {len(texts)} documents.")

    if not texts:
        print("❌ No valid texts extracted. Aborting embedding generation.")
        return {"success": False, "error": "No valid texts extracted"}

    # Load model and generate embeddings
    print("Loading sentence transformer model...")
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    
    print("Generating embeddings...")
    embeddings = model.encode(texts, batch_size=16, show_progress_bar=True, convert_to_numpy=True)

    # Normalize embeddings (important for cosine similarity)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    # Create FAISS index
    print("Creating FAISS index...")
    d = embeddings.shape[1]  # dimension = 768
    index = faiss.IndexFlatIP(d)  # inner product = cosine similarity with normalized vectors
    index.add(embeddings)

    # Save index and mapping
    store_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faiss_store")
    os.makedirs(store_dir, exist_ok=True)
    
    faiss.write_index(index, os.path.join(store_dir, "legal_cases.index"))

    with open(os.path.join(store_dir, "id2name.json"), "w") as f:
        json.dump(file_names, f)

    print("✅ FAISS index and metadata saved successfully.")
    print(f"✅ Index contains {len(texts)} documents.")
    
    # Optionally upload to Azure
    if connection_string:
        print("🔄 Uploading to Azure Blob Storage...")
        azure_helper = get_azure_blob_helper(connection_string)
        
        index_path = os.path.join(store_dir, "legal_cases.index")
        id2name_path = os.path.join(store_dir, "id2name.json")
        
        if azure_helper.upload_faiss_index(index_path, id2name_path):
            print("✅ FAISS index uploaded to Azure Blob Storage successfully.")
        else:
            print("⚠️  Failed to upload FAISS index to Azure Blob Storage.")
    
    return {
        "success": True,
        "documents_processed": len(texts),
        "index_dimension": d,
        "local_path": store_dir
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate embeddings for legal documents")
    parser.add_argument("--azure", action="store_true", help="Use Azure Blob Storage")
    parser.add_argument("--max-files", type=int, help="Maximum number of files to process")
    parser.add_argument("--pdf-dir", type=str, help="Local PDF directory path")
    
    args = parser.parse_args()
    
    # Generate embeddings when this file is run directly
    result = generate_embeddings(
        pdf_dir_path=args.pdf_dir,
        max_files=args.max_files,
        use_azure=args.azure
    )
    
    if not result["success"]:
        print(f"❌ Embedding generation failed: {result.get('error', 'Unknown error')}")
        exit(1)
    else:
        print("🎉 Embedding generation completed successfully!")
