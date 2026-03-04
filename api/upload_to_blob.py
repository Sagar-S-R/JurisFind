"""
Run this once to upload FAISS index files to Azure Blob Storage.
Usage: python upload_to_blob.py
"""
import os
from azure.storage.blob import BlobServiceClient

# ── Paste your connection string here ──────────────────────────────────────────
CONNECTION_STRING = "YOUR_CONNECTION_STRING_HERE"
CONTAINER_NAME = "data"
# ───────────────────────────────────────────────────────────────────────────────

FILES = {
    "faiss_store/legal_cases.index": r"e:\Sagar\AI_ML_DL_DS\projects\legal-case\JurisFind\api\data\faiss_store\legal_cases.index",
    "faiss_store/id2name.json":      r"e:\Sagar\AI_ML_DL_DS\projects\legal-case\JurisFind\api\data\faiss_store\id2name.json",
}

def upload():
    client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container = client.get_container_client(CONTAINER_NAME)

    # Create container if it doesn't exist
    try:
        container.create_container()
        print(f"Created container: {CONTAINER_NAME}")
    except Exception:
        print(f"Container '{CONTAINER_NAME}' already exists.")

    for blob_name, local_path in FILES.items():
        size_mb = os.path.getsize(local_path) / (1024 * 1024)
        print(f"Uploading {blob_name} ({size_mb:.1f} MB)...")
        with open(local_path, "rb") as f:
            container.upload_blob(blob_name, f, overwrite=True)
        print(f"  ✓ Done")

    print("\nAll files uploaded successfully!")
    print(f"Blobs in container '{CONTAINER_NAME}':")
    for blob in container.list_blobs():
        print(f"  - {blob.name}")

if __name__ == "__main__":
    if CONNECTION_STRING == "YOUR_CONNECTION_STRING_HERE":
        print("ERROR: Set your CONNECTION_STRING in this script first.")
    else:
        upload()
