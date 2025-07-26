"""
Confidential PDF Upload and Processing Service
"""
import os
import tempfile
import shutil
from typing import Dict, Any, List
from fastapi import UploadFile
import fitz  # PyMuPDF
from search_service import get_searcher
from legal_agent import get_agent

class ConfidentialPDFProcessor:
    def __init__(self):
        """Initialize the confidential PDF processor"""
        self.temp_dir = tempfile.mkdtemp(prefix="confidential_pdfs_")
        
    def save_uploaded_file(self, upload_file: UploadFile) -> str:
        """Save uploaded PDF to temporary directory"""
        try:
            # Create unique filename
            temp_filename = f"confidential_{upload_file.filename}"
            temp_path = os.path.join(self.temp_dir, temp_filename)
            
            # Save uploaded file
            with open(temp_path, "wb") as buffer:
                content = upload_file.file.read()
                buffer.write(content)
            
            # Reset file pointer for potential future reads
            upload_file.file.seek(0)
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Error saving uploaded file: {str(e)}")
    
    def extract_text_from_uploaded_pdf(self, file_path: str) -> str:
        """Extract text from uploaded PDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from uploaded PDF: {str(e)}")
    
    def retrieve_similar_cases(self, uploaded_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar cases from existing datastore"""
        try:
            searcher = get_searcher()
            
            # Use the uploaded text as search query - take first 1500 chars for better search
            search_query = uploaded_text[:1500].strip()
            if not search_query:
                raise Exception("No readable text found in uploaded PDF")
            
            results = searcher.search(search_query, top_k=top_k)
            
            return results
            
        except Exception as e:
            raise Exception(f"Error retrieving similar cases: {str(e)}")
    
    def analyze_uploaded_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Analyze uploaded document using the legal agent"""
        try:
            agent = get_agent()
            result = agent.analyze_document(file_path, f"confidential_{filename}")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": "Document analysis failed"
            }
    
    def answer_question_uploaded(self, filename: str, question: str) -> str:
        """Answer question about uploaded document"""
        try:
            agent = get_agent()
            confidential_filename = f"confidential_{filename}"
            answer = agent.answer_question(confidential_filename, question)
            
            return answer
            
        except Exception as e:
            raise Exception(f"Error answering question: {str(e)}")
    
    def cleanup_uploaded_file(self, filename: str) -> Dict[str, Any]:
        """Clean up uploaded file and its embeddings"""
        try:
            agent = get_agent()
            confidential_filename = f"confidential_{filename}"
            
            # Clean up embeddings
            agent.cleanup_temp_embeddings(confidential_filename)
            
            # Clean up physical file
            temp_path = os.path.join(self.temp_dir, confidential_filename)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                "success": True,
                "message": f"Cleaned up confidential file: {filename}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Cleanup failed"
            }
    
    def get_upload_stats(self, filename: str) -> Dict[str, Any]:
        """Get stats about uploaded document"""
        try:
            agent = get_agent()
            confidential_filename = f"confidential_{filename}"
            stats = agent.get_document_stats(confidential_filename)
            
            return {
                "success": True,
                "filename": filename,
                "has_analysis": stats["has_embeddings"],
                "is_confidential": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "has_analysis": False,
                "is_confidential": True
            }

# Global processor instance
pdf_processor = None

def get_pdf_processor():
    """Get or create the global PDF processor instance"""
    global pdf_processor
    if pdf_processor is None:
        pdf_processor = ConfidentialPDFProcessor()
    return pdf_processor
