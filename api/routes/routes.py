from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import sys, os
import io

# Ensure api/ is on sys.path for namespace package imports
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from services.search_service import get_searcher
from agents.legal_agent import get_agent
from agents.legal_chatbot import get_legal_chatbot
from confidential.confidential_pdf import get_pdf_processor
from helpers.azure_blob_helper import get_azure_blob_helper

# Create router for API routes
router = APIRouter()

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SearchResult(BaseModel):
    filename: str
    score: float
    similarity_percentage: float

class SearchResponse(BaseModel):
    success: bool
    query: str
    results: list[SearchResult]
    total_results: int

class CaseDetails(BaseModel):
    filename: str
    path: Optional[str] = None
    size: Optional[int] = None
    exists: bool

class HealthResponse(BaseModel):
    status: str
    message: str
    total_cases: int

class QuestionRequest(BaseModel):
    filename: str
    question: str

class AnalysisResponse(BaseModel):
    success: bool
    filename: str
    text_length: int
    embedding_status: str
    summary: str
    message: str

class QuestionResponse(BaseModel):
    success: bool
    filename: str
    question: str
    answer: str

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    success: bool
    response: str
    is_legal: bool
    domain_filtered: bool

class UploadResponse(BaseModel):
    success: bool
    filename: str
    message: str

class RetrieveResponse(BaseModel):
    success: bool
    filename: str
    similar_cases: list
    total_found: int

@router.post("/search", response_model=SearchResponse)
async def search_cases(request: SearchRequest):
    """Search for legal cases based on query text."""
    try:
        query_text = request.query.strip()
        if not query_text:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        # Validate top_k parameter
        top_k = request.top_k
        if not isinstance(top_k, int) or top_k < 1 or top_k > 50:
            top_k = 5
        
        # Get searcher and perform search
        searcher = get_searcher()
        results = searcher.search(query_text, top_k=top_k)
        
        # Convert results to Pydantic models
        search_results = [SearchResult(**result) for result in results]
        
        return SearchResponse(
            success=True,
            query=query_text,
            results=search_results,
            total_results=len(search_results)
        )
    
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Search service not available: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/case/{filename}")
async def get_case_details(filename: str):
    """Get details about a specific case file."""
    try:
        searcher = get_searcher()
        details = searcher.get_case_details(filename)
        
        if details['exists']:
            return {
                'success': True,
                'case_details': CaseDetails(**details)
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f'Case file {filename} does not exist'
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get case details: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        searcher = get_searcher()
        return HealthResponse(
            status='healthy',
            message='Legal case search service is running',
            total_cases=len(searcher.id2name) if searcher.id2name else 0
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@router.get("/search", response_model=SearchResponse)
async def search_cases_get(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results to return", ge=1, le=50)
):
    """GET endpoint for simple search queries."""
    try:
        query_text = q.strip()
        if not query_text:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        searcher = get_searcher()
        results = searcher.search(query_text, top_k=top_k)
        
        # Convert results to Pydantic models
        search_results = [SearchResult(**result) for result in results]
        
        return SearchResponse(
            success=True,
            query=query_text,
            results=search_results,
            total_results=len(search_results)
        )
    
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Search service not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/pdf/{filename}")
async def get_pdf_file(filename: str):
    """Serve PDF files from Azure Blob Storage or local files."""
    try:
        # Try Azure Blob Storage first
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        if connection_string:
            azure_helper = get_azure_blob_helper(connection_string)
            
            # Check if PDF exists in Azure
            pdf_blob_name = f"pdfs/{filename}"
            if azure_helper.blob_exists(pdf_blob_name):
                # Download PDF data from Azure
                pdf_data = azure_helper.download_file_data(pdf_blob_name)
                
                if pdf_data:
                    return StreamingResponse(
                        io.BytesIO(pdf_data),
                        media_type="application/pdf",
                        headers={"Content-Disposition": f"inline; filename={filename}"}
                    )
        
        # Fallback to local files
        pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "pdfs"))
        pdf_path = os.path.join(pdf_dir, filename)
        
        if os.path.exists(pdf_path):
            return FileResponse(
                path=pdf_path,
                media_type="application/pdf",
                filename=filename
            )
        
        # File not found in either location
        raise HTTPException(
            status_code=404,
            detail=f"PDF file '{filename}' not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error serving PDF: {str(e)}"
        )

@router.get("/list-pdfs")
async def list_pdf_files():
    """List all PDF files available in Azure Blob Storage or local storage."""
    try:
        # Try Azure Blob Storage first
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        if connection_string:
            azure_helper = get_azure_blob_helper(connection_string)
            pdf_files = azure_helper.list_pdf_files()
            
            return {
                "success": True,
                "source": "azure",
                "total_files": len(pdf_files),
                "files": pdf_files
            }
        
        # Fallback to local files
        pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "pdfs"))
        
        if os.path.exists(pdf_dir):
            pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
            
            return {
                "success": True,
                "source": "local",
                "total_files": len(pdf_files),
                "files": pdf_files
            }
        
        return {
            "success": False,
            "error": "No PDF files found in either Azure or local storage"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing PDF files: {str(e)}"
        )

@router.post("/upload-pdf-to-azure")
async def upload_pdf_to_azure(file: UploadFile = File(...)):
    """Upload a PDF file to Azure Blob Storage"""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise HTTPException(status_code=500, detail="Azure Storage not configured")
        
        azure_helper = get_azure_blob_helper(connection_string)
        
        # Read file data
        file_data = await file.read()
        
        # Upload to Azure
        blob_name = f"pdfs/{file.filename}"
        success = azure_helper.upload_file_data(file_data, blob_name)
        
        if success:
            return {
                "success": True,
                "filename": file.filename,
                "blob_name": blob_name,
                "size": len(file_data),
                "message": "PDF uploaded to Azure Blob Storage successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upload PDF to Azure")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading PDF: {str(e)}"
        )

@router.post("/generate-embeddings-from-azure")
async def generate_embeddings_from_azure(max_files: Optional[int] = None):
    """Generate FAISS embeddings from PDFs in Azure Blob Storage"""
    try:
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise HTTPException(status_code=500, detail="Azure Storage not configured")
        
        from helpers.azure_blob_helper import generate_and_upload_faiss_index
        
        # Generate embeddings from Azure PDFs
        result = generate_and_upload_faiss_index(
            connection_string=connection_string,
            max_files=max_files
        )
        
        if result["success"]:
            return {
                "success": True,
                "documents_processed": result["documents_processed"],
                "index_dimension": result["index_dimension"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating embeddings: {str(e)}"
        )

# Agent-based routes for document analysis
@router.post("/analyze-document", response_model=AnalysisResponse)
async def analyze_document(filename: str):
    """Analyze a legal document using the LangChain agent."""
    import tempfile
    try:
        # Get Azure connection string
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise HTTPException(status_code=500, detail="Azure storage not configured")
        
        # Get Azure blob helper
        azure_helper = get_azure_blob_helper(connection_string)
        
        # Check if file exists in Azure
        if not azure_helper.blob_exists("data", f"pdfs/{filename}"):
            raise HTTPException(status_code=404, detail="PDF not found in Azure storage")
        
        # Download PDF content to memory for analysis
        pdf_content = azure_helper.download_blob("data", f"pdfs/{filename}")
        
        # Create temporary file for agent analysis
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_path = temp_file.name
        
        try:
            agent = get_agent()
            result = agent.analyze_document(temp_path, filename)
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return AnalysisResponse(**result)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about a specific document."""
    try:
        agent = get_agent()
        answer = agent.answer_question(request.filename, request.question)
        
        return QuestionResponse(
            success=True,
            filename=request.filename,
            question=request.question,
            answer=answer
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/document-stats/{filename}")
async def get_document_stats(filename: str):
    """Get statistics about an analyzed document."""
    try:
        agent = get_agent()
        stats = agent.get_document_stats(filename)
        
        return {
            "success": True,
            "filename": filename,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup-embeddings/{filename}")
async def cleanup_embeddings(filename: str):
    """Clean up temporary embeddings for a document."""
    try:
        agent = get_agent()
        agent.cleanup_temp_embeddings(filename)
        
        return {
            "success": True,
            "message": f"Cleaned up embeddings for {filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legal Chatbot routes
@router.post("/legal-chat", response_model=ChatResponse)
async def legal_chat(request: ChatRequest):
    """Chat with the legal AI assistant (legal domain only)."""
    try:
        chatbot = get_legal_chatbot()
        result = chatbot.chat(request.question)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Chat failed"))
        
        return ChatResponse(
            success=result["success"],
            response=result["response"],
            is_legal=result["is_legal"],
            domain_filtered=result.get("domain_filtered", False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/legal-chat/clear")
async def clear_chat_history():
    """Clear the legal chatbot history."""
    try:
        chatbot = get_legal_chatbot()
        result = chatbot.clear_history()
        
        return {
            "success": True,
            "message": "Chat history cleared successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/legal-chat/stats")
async def get_chat_stats():
    """Get legal chatbot statistics."""
    try:
        chatbot = get_legal_chatbot()
        stats = chatbot.get_chat_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Confidential PDF Upload routes
@router.post("/upload-confidential-pdf", response_model=UploadResponse)
async def upload_confidential_pdf(file: UploadFile = File(...)):
    """Upload a confidential PDF for analysis."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        processor = get_pdf_processor()
        processor.save_uploaded_file(file)
        
        return UploadResponse(
            success=True,
            filename=file.filename,
            message="Confidential PDF uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrieve-similar-cases", response_model=RetrieveResponse)
async def retrieve_similar_cases(filename: str, top_k: int = 5):
    """Retrieve similar cases from datastore based on uploaded PDF."""
    try:
        processor = get_pdf_processor()
        temp_path = os.path.join(processor.temp_dir, f"confidential_{filename}")
        
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="Uploaded PDF not found. Please upload again.")
        
        # Extract text from uploaded PDF
        uploaded_text = processor.extract_text_from_uploaded_pdf(temp_path)
        
        # Retrieve similar cases
        similar_cases = processor.retrieve_similar_cases(uploaded_text, top_k)
        
        return RetrieveResponse(
            success=True,
            filename=filename,
            similar_cases=similar_cases,
            total_found=len(similar_cases)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-confidential-pdf", response_model=AnalysisResponse)
async def analyze_confidential_pdf(filename: str):
    """Analyze uploaded confidential PDF."""
    try:
        processor = get_pdf_processor()
        temp_path = os.path.join(processor.temp_dir, f"confidential_{filename}")
        
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="Uploaded PDF not found. Please upload again.")
        
        result = processor.analyze_uploaded_document(temp_path, filename)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return AnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask-question-confidential", response_model=QuestionResponse)
async def ask_question_confidential(request: QuestionRequest):
    """Ask question about uploaded confidential PDF."""
    try:
        processor = get_pdf_processor()
        answer = processor.answer_question_uploaded(request.filename, request.question)
        
        return QuestionResponse(
            success=True,
            filename=request.filename,
            question=request.question,
            answer=answer
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup-confidential/{filename}")
async def cleanup_confidential_pdf(filename: str):
    """Clean up confidential PDF and its embeddings."""
    try:
        processor = get_pdf_processor()
        return processor.cleanup_uploaded_file(filename)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/confidential-stats/{filename}")
async def get_confidential_stats(filename: str):
    """Get stats about uploaded confidential PDF."""
    try:
        processor = get_pdf_processor()
        stats = processor.get_upload_stats(filename)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
