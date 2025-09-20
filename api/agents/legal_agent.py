"""
Legal Document Analysis Agent using LangChain and Groq
"""
import os
import json
import fitz  # PyMuPDF
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LegalDocumentAgent:
    def __init__(self):
        """Initialize the Legal Document Analysis Agent"""
        # Initialize Groq client
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Temporary vector stores for individual documents
        self.temp_vector_stores = {}
        
        # Chat templates
        self.summary_template = ChatPromptTemplate.from_template("""
        You are a legal expert AI assistant specializing in analyzing legal documents. 
        Your task is to provide a comprehensive summary of the given legal document.

        Document Content:
        {document_text}

        Please provide a detailed summary covering:
        1. **Document Type & Overview**: What type of legal document this is
        2. **Key Parties**: Main parties involved (if applicable)
        3. **Main Legal Issues**: Primary legal matters discussed
        4. **Key Facts**: Important factual information
        5. **Legal Principles**: Relevant laws, statutes, or precedents mentioned
        6. **Conclusion/Outcome**: Final decision, ruling, or conclusion (if applicable)
        7. **Significance**: Why this document/case is important

        Provide a clear, professional summary in a structured format. Use legal terminology appropriately but ensure it's understandable.
        """)
        
        self.qa_template = ChatPromptTemplate.from_template("""
        You are a legal expert AI assistant. You have access to a specific legal document and must answer questions based ONLY on the information contained in that document.

        Context from the document:
        {context}

        Question: {question}

        Instructions:
        1. Answer based ONLY on the information provided in the context
        2. If the answer is not in the document, clearly state "This information is not available in the provided document"
        3. Use specific quotes or references from the document when possible
        4. Provide detailed, professional legal analysis
        5. If relevant, explain the legal implications or significance

        Answer:
        """)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def create_temp_embeddings(self, filename: str, text: str) -> str:
        """Create temporary embeddings for a specific document"""
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                raise ValueError("No text chunks created from document")
            
            # Create temporary vector store
            vector_store = FAISS.from_texts(chunks, self.embeddings)
            
            # Store in memory with filename as key
            self.temp_vector_stores[filename] = vector_store
            
            return f"Created temporary embeddings for {filename} with {len(chunks)} chunks"
            
        except Exception as e:
            raise Exception(f"Error creating embeddings: {str(e)}")

    def generate_summary(self, text: str) -> str:
        """Generate comprehensive summary of the legal document"""
        try:
            # Format the prompt
            prompt = self.summary_template.format(document_text=text[:8000])  # Limit to avoid token limits
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",  # Using Llama3 70B - reliable and supported
                messages=[
                    {"role": "system", "content": "You are a legal expert AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent legal analysis
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    def answer_question(self, filename: str, question: str) -> str:
        """Answer question based on document embeddings"""
        try:
            if filename not in self.temp_vector_stores:
                raise ValueError(f"No embeddings found for {filename}. Please analyze the document first.")
            
            # Retrieve relevant context
            vector_store = self.temp_vector_stores[filename]
            retriever = vector_store.as_retriever(search_kwargs={"k": 4})
            relevant_docs = retriever.get_relevant_documents(question)
            
            # Combine context
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Format prompt
            prompt = self.qa_template.format(context=context, question=question)
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a legal expert AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error answering question: {str(e)}")

    def analyze_document(self, pdf_path: str, filename: str) -> Dict[str, Any]:
        """Complete document analysis pipeline"""
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text:
                raise ValueError("No text could be extracted from the PDF")
            
            # Create embeddings
            embedding_status = self.create_temp_embeddings(filename, text)
            
            # Generate summary
            summary = self.generate_summary(text)
            
            return {
                "success": True,
                "filename": filename,
                "text_length": len(text),
                "embedding_status": embedding_status,
                "summary": summary,
                "message": "Document analyzed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": "Document analysis failed"
            }

    def get_document_stats(self, filename: str) -> Dict[str, Any]:
        """Get statistics about the analyzed document"""
        if filename in self.temp_vector_stores:
            vector_store = self.temp_vector_stores[filename]
            return {
                "has_embeddings": True,
                "chunk_count": vector_store.index.ntotal,
                "embedding_dimension": vector_store.index.d
            }
        else:
            return {
                "has_embeddings": False,
                "chunk_count": 0,
                "embedding_dimension": 0
            }

    def cleanup_temp_embeddings(self, filename: str = None):
        """Clean up temporary embeddings"""
        if filename:
            if filename in self.temp_vector_stores:
                del self.temp_vector_stores[filename]
        else:
            # Clean up all
            self.temp_vector_stores.clear()

# Global agent instance
agent = None

def get_agent():
    """Get or create the global agent instance"""
    global agent
    if agent is None:
        agent = LegalDocumentAgent()
    return agent
