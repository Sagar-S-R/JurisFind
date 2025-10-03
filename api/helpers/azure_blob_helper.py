"""
Azure Blob Storage Helper for Legal Case Document Management

This module provides comprehensive Azure Blob Storage integration for:
- PDF document upload/download
- FAISS index file management
- Blob listing and metadata operations
"""

import os
import tempfile
import json
from typing import List, Dict, Any, Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, AzureError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureBlobHelper:
    """Helper class for Azure Blob Storage operations."""
    
    def __init__(self, connection_string: str = None, container_name: str = "data"):
        """
        Initialize Azure Blob Storage client.
        
        Args:
            connection_string: Azure Storage connection string (from env if None)
            container_name: Container name (default: "data")
        """
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = container_name
        
        if not self.connection_string:
            raise ValueError("Azure Storage connection string is required")
        
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Create container if it doesn't exist
            try:
                self.container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
            except Exception:
                # Container likely already exists
                pass
                
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage client: {e}")
            raise
    
    def upload_file(self, local_file_path: str, blob_name: str, overwrite: bool = True) -> bool:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            local_file_path: Path to local file
            blob_name: Target blob name (path in container)
            overwrite: Whether to overwrite existing blob
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(local_file_path, "rb") as data:
                self.container_client.upload_blob(
                    name=blob_name,
                    data=data,
                    overwrite=overwrite
                )
            logger.info(f"Uploaded {local_file_path} to {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload {local_file_path}: {e}")
            return False
    
    def upload_file_data(self, file_data: bytes, blob_name: str, overwrite: bool = True) -> bool:
        """
        Upload file data directly to Azure Blob Storage.
        
        Args:
            file_data: File data as bytes
            blob_name: Target blob name (path in container)
            overwrite: Whether to overwrite existing blob
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.container_client.upload_blob(
                name=blob_name,
                data=file_data,
                overwrite=overwrite
            )
            logger.info(f"Uploaded data to {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload data to {blob_name}: {e}")
            return False
    
    def download_file(self, blob_name: str, local_file_path: str) -> bool:
        """
        Download a file from Azure Blob Storage.
        
        Args:
            blob_name: Source blob name
            local_file_path: Target local file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            with open(local_file_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())
            
            logger.info(f"Downloaded {blob_name} to {local_file_path}")
            return True
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            return False
    
    def download_file_data(self, blob_name: str) -> Optional[bytes]:
        """
        Download file data from Azure Blob Storage.
        
        Args:
            blob_name: Source blob name
            
        Returns:
            bytes: File data if successful, None otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            download_stream = blob_client.download_blob()
            return download_stream.readall()
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            return None
        except Exception as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            return None
    
    def download_pdf_to_temp_file(self, pdf_filename: str) -> Optional[str]:
        """
        Download a PDF from the pdfs/ directory to a temporary file.
        
        Args:
            pdf_filename: Name of the PDF file
            
        Returns:
            str: Path to temporary file if successful, None otherwise
        """
        blob_name = f"pdfs/{pdf_filename}"
        
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            # Download to temp file
            if self.download_file(blob_name, temp_path):
                return temp_path
            else:
                # Clean up on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass
                return None
                
        except Exception as e:
            logger.error(f"Failed to download PDF {pdf_filename}: {e}")
            return None
    
    def list_blobs_in_directory(self, directory: str = "") -> List[str]:
        """
        List all blobs in a directory.
        
        Args:
            directory: Directory prefix (e.g., "pdfs/")
            
        Returns:
            List[str]: List of blob names
        """
        try:
            if directory and not directory.endswith("/"):
                directory += "/"
            
            blobs = []
            for blob in self.container_client.list_blobs(name_starts_with=directory):
                # Remove directory prefix from blob name
                blob_name = blob.name
                if directory:
                    blob_name = blob_name[len(directory):]
                
                # Skip empty names (directory markers)
                if blob_name:
                    blobs.append(blob_name)
            
            return blobs
            
        except Exception as e:
            logger.error(f"Failed to list blobs in {directory}: {e}")
            return []
    
    def list_pdf_files(self) -> List[str]:
        """
        List all PDF files in the pdfs/ directory.
        
        Returns:
            List[str]: List of PDF filenames
        """
        return [f for f in self.list_blobs_in_directory("pdfs") if f.lower().endswith('.pdf')]
    
    def blob_exists(self, blob_name: str) -> bool:
        """
        Check if a blob exists.
        
        Args:
            blob_name: Blob name to check
            
        Returns:
            bool: True if blob exists, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            return blob_client.exists()
        except Exception:
            return False
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob.
        
        Args:
            blob_name: Blob name to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {blob_name}")
            return True  # Consider non-existent as successfully deleted
        except Exception as e:
            logger.error(f"Failed to delete blob {blob_name}: {e}")
            return False
    
    def download_faiss_index(self, temp_dir: str = None) -> Optional[Dict[str, str]]:
        """
        Download FAISS index files from Azure Blob Storage.
        
        Args:
            temp_dir: Temporary directory (creates one if None)
            
        Returns:
            Dict[str, str]: Paths to downloaded files or None if failed
        """
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="faiss_data_")
        
        try:
            # Download FAISS index file
            index_blob = "faiss_store/legal_cases.index"
            index_path = os.path.join(temp_dir, "legal_cases.index")
            
            if not self.download_file(index_blob, index_path):
                logger.error("Failed to download FAISS index file")
                return None
            
            # Download ID to name mapping
            id2name_blob = "faiss_store/id2name.json"
            id2name_path = os.path.join(temp_dir, "id2name.json")
            
            if not self.download_file(id2name_blob, id2name_path):
                logger.error("Failed to download ID to name mapping")
                return None
            
            return {
                "index_path": index_path,
                "id2name_path": id2name_path,
                "temp_dir": temp_dir
            }
            
        except Exception as e:
            logger.error(f"Failed to download FAISS index: {e}")
            return None
    
    def upload_faiss_index(self, index_path: str, id2name_path: str) -> bool:
        """
        Upload FAISS index files to Azure Blob Storage.
        
        Args:
            index_path: Path to FAISS index file
            id2name_path: Path to ID to name mapping file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Upload FAISS index
            if not self.upload_file(index_path, "faiss_store/legal_cases.index"):
                return False
            
            # Upload ID to name mapping
            if not self.upload_file(id2name_path, "faiss_store/id2name.json"):
                return False
            
            logger.info("Successfully uploaded FAISS index to Azure Blob Storage")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload FAISS index: {e}")
            return False
    
    def get_blob_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a blob.
        
        Args:
            blob_name: Blob name
            
        Returns:
            Dict[str, Any]: Blob metadata or None if failed
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            properties = blob_client.get_blob_properties()
            
            return {
                "name": blob_name,
                "size": properties.size,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type,
                "etag": properties.etag
            }
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {blob_name}: {e}")
            return None


# Global instance
_azure_blob_helper = None

def get_azure_blob_helper(connection_string: str = None, container_name: str = "data") -> AzureBlobHelper:
    """
    Get or create global Azure Blob Helper instance.
    
    Args:
        connection_string: Azure Storage connection string
        container_name: Container name
        
    Returns:
        AzureBlobHelper: Global instance
    """
    global _azure_blob_helper
    
    if _azure_blob_helper is None:
        _azure_blob_helper = AzureBlobHelper(connection_string, container_name)
    
    return _azure_blob_helper


def upload_pdf_files_to_azure(local_pdf_dir: str, connection_string: str = None) -> Dict[str, Any]:
    """
    Batch upload PDF files from local directory to Azure Blob Storage.
    
    Args:
        local_pdf_dir: Local PDF directory path
        connection_string: Azure Storage connection string
        
    Returns:
        Dict[str, Any]: Upload results
    """
    azure_helper = get_azure_blob_helper(connection_string)
    
    if not os.path.exists(local_pdf_dir):
        return {"success": False, "error": f"Directory not found: {local_pdf_dir}"}
    
    pdf_files = [f for f in os.listdir(local_pdf_dir) if f.lower().endswith('.pdf')]
    
    results = {
        "success": True,
        "total_files": len(pdf_files),
        "uploaded": 0,
        "failed": 0,
        "errors": []
    }
    
    for pdf_file in pdf_files:
        local_path = os.path.join(local_pdf_dir, pdf_file)
        blob_name = f"pdfs/{pdf_file}"
        
        if azure_helper.upload_file(local_path, blob_name):
            results["uploaded"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(f"Failed to upload: {pdf_file}")
    
    logger.info(f"Upload complete: {results['uploaded']}/{results['total_files']} files uploaded")
    return results


def generate_and_upload_faiss_index(local_pdf_dir: str = None, connection_string: str = None, max_files: int = None) -> Dict[str, Any]:
    """
    Generate FAISS index from Azure PDFs and upload to Azure Blob Storage.
    
    Args:
        local_pdf_dir: Local PDF directory (for initial upload if needed)
        connection_string: Azure Storage connection string
        max_files: Maximum number of files to process
        
    Returns:
        Dict[str, Any]: Generation results
    """
    try:
        # Import required modules
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
        import fitz  # PyMuPDF
        from tqdm import tqdm
        
        azure_helper = get_azure_blob_helper(connection_string)
        
        # Get list of PDF files from Azure
        pdf_files = azure_helper.list_pdf_files()
        
        if not pdf_files:
            return {"success": False, "error": "No PDF files found in Azure Blob Storage"}
        
        if max_files:
            pdf_files = pdf_files[:max_files]
        
        logger.info(f"Processing {len(pdf_files)} PDF files from Azure Blob Storage")
        
        # Extract text from PDFs
        texts = []
        file_names = []
        
        for pdf_file in tqdm(pdf_files, desc="Extracting text from PDFs"):
            # Download PDF to temporary file
            temp_pdf_path = azure_helper.download_pdf_to_temp_file(pdf_file)
            
            if temp_pdf_path:
                try:
                    # Extract text from PDF
                    doc = fitz.open(temp_pdf_path)
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    
                    if text.strip():
                        texts.append(text)
                        file_names.append(pdf_file)
                    
                except Exception as e:
                    logger.error(f"Error processing {pdf_file}: {e}")
                
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_pdf_path)
                    except:
                        pass
        
        if not texts:
            return {"success": False, "error": "No valid texts extracted from PDFs"}
        
        logger.info(f"Extracted text from {len(texts)} documents")
        
        # Generate embeddings
        logger.info("Loading sentence transformer model...")
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        
        logger.info("Generating embeddings...")
        embeddings = model.encode(texts, batch_size=16, show_progress_bar=True, convert_to_numpy=True)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Create FAISS index
        logger.info("Creating FAISS index...")
        d = embeddings.shape[1]  # dimension
        index = faiss.IndexFlatIP(d)  # inner product = cosine similarity with normalized vectors
        index.add(embeddings)
        
        # Save to temporary files
        temp_dir = tempfile.mkdtemp(prefix="faiss_generation_")
        index_path = os.path.join(temp_dir, "legal_cases.index")
        id2name_path = os.path.join(temp_dir, "id2name.json")
        
        faiss.write_index(index, index_path)
        
        with open(id2name_path, "w") as f:
            json.dump(file_names, f)
        
        # Upload to Azure Blob Storage
        if azure_helper.upload_faiss_index(index_path, id2name_path):
            # Clean up temporary files
            try:
                os.unlink(index_path)
                os.unlink(id2name_path)
                os.rmdir(temp_dir)
            except:
                pass
            
            return {
                "success": True,
                "documents_processed": len(texts),
                "index_dimension": d,
                "message": "FAISS index generated and uploaded to Azure Blob Storage successfully"
            }
        else:
            return {"success": False, "error": "Failed to upload FAISS index to Azure Blob Storage"}
    
    except Exception as e:
        logger.error(f"Error generating FAISS index: {e}")
        return {"success": False, "error": str(e)}