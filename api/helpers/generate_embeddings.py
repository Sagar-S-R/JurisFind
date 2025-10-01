import fitz 
from tqdm import tqdm
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        return " ".join(text.split())  
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return ""

def generate_embeddings(pdf_dir_path=None, max_files=None):
    """Generate embeddings for PDF files and save to FAISS index."""
    
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
        return

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

if __name__ == "__main__":
    # Generate embeddings when this file is run directly
    generate_embeddings()
