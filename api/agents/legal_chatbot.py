"""
Legal Chatbot Agent using LangChain and Groq
Specialized for judicial and legal domain questions
"""
import os
from pathlib import Path
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from groq import Groq
from dotenv import load_dotenv
import re

# Load environment variables explicitly from api/.env (alongside this file)
_dotenv_path = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=_dotenv_path, override=False)

class LegalChatbotAgent:
    def __init__(self):
        """Initialize the Legal Chatbot Agent"""
        # Initialize Groq client
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        # Trim accidental surrounding quotes or whitespace
        if self.groq_api_key:
            self.groq_api_key = self.groq_api_key.strip().strip('\"').strip("'")
        # Masked log of key presence for diagnostics
        try:
            masked = (
                f"{self.groq_api_key[:4]}...{self.groq_api_key[-4:]}"
                if self.groq_api_key and len(self.groq_api_key) >= 8 else "(missing or too short)"
            )
            print(f"GROQ_API_KEY detected: {masked} | .env path: {_dotenv_path}")
        except Exception:
            pass
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        # Load model from environment
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        # Chat history for context
        self.chat_history = []
        
        # Legal domain filter template
        self.domain_filter_template = ChatPromptTemplate.from_template("""
        You are a domain filter for a legal AI assistant. Your task is to determine if a question is related to the judicial system, legal matters, or law.

        Question: {question}

        Respond with ONLY "LEGAL" if the question is about:
        - Laws, statutes, regulations
        - Court procedures, judicial processes
        - Legal concepts, terminology
        - Rights, obligations, legal remedies
        - Legal cases, precedents
        - Legal professions (judges, lawyers, etc.)
        - Constitutional matters
        - Legal documentation
        - Criminal, civil, corporate, or any area of law

        Respond with ONLY "NON-LEGAL" if the question is about:
        - General knowledge not related to law
        - Personal advice unrelated to legal matters
        - Technology, science, entertainment (unless legally relevant)
        - Casual conversation
        - Non-legal professional advice

        Response:
        """)
        
        # Legal chatbot response template
        self.legal_chat_template = ChatPromptTemplate.from_template("""
        You are an expert legal AI assistant specializing in the judicial system and legal matters. You provide accurate, professional, and helpful information about law and legal processes.

        Chat History:
        {chat_history}

        Current Question: {question}

        Guidelines:
        1. Provide accurate legal information and explanations
        2. Use appropriate legal terminology but explain complex concepts
        3. Mention when legal advice should be sought from a qualified attorney
        4. Reference relevant laws, cases, or legal principles when applicable
        5. Be professional and authoritative in your responses
        6. If you're unsure about specific legal details, acknowledge limitations
        7. Focus on educational and informational content about law

        Important: This is for informational purposes only and does not constitute legal advice.

        Response:
        """)

    def clean_ai_response(self, response: str) -> str:
        """Clean AI response by removing unwanted formatting and artifacts"""
        if not response:
            return response
            
        # Remove common AI artifacts and formatting issues
        cleaned = response.strip()
        
        # Remove markdown bold/italic artifacts that aren't meant for display
        cleaned = re.sub(r'\*\*\s*\([^)]*content[^)]*\)\s*\*\*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\*\*\s*\(content\)\s*\*\*', '', cleaned, flags=re.IGNORECASE)
        
        # Remove system prompt leakage
        cleaned = re.sub(r'^(System:|Assistant:|AI:|Response:)\s*', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove excessive whitespace and newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r' {2,}', ' ', cleaned)
        
        # Remove markdown formatting that's not meant for display
        cleaned = re.sub(r'^\*\*.*?\*\*$', '', cleaned, flags=re.MULTILINE)  # Remove standalone bold lines
        
        # Clean up any remaining artifacts
        cleaned = cleaned.strip()
        
        return cleaned
        
        # Legal domain filter template
        self.domain_filter_template = ChatPromptTemplate.from_template("""
        You are a domain filter for a legal AI assistant. Your task is to determine if a question is related to the judicial system, legal matters, or law.

        Question: {question}

        Respond with ONLY "LEGAL" if the question is about:
        - Laws, statutes, regulations
        - Court procedures, judicial processes
        - Legal concepts, terminology
        - Rights, obligations, legal remedies
        - Legal cases, precedents
        - Legal professions (judges, lawyers, etc.)
        - Constitutional matters
        - Legal documentation
        - Criminal, civil, corporate, or any area of law

        Respond with ONLY "NON-LEGAL" if the question is about:
        - General knowledge not related to law
        - Personal advice unrelated to legal matters
        - Technology, science, entertainment (unless legally relevant)
        - Casual conversation
        - Non-legal professional advice

        Response:
        """)

    def is_legal_question(self, question: str) -> bool:
        """Filter to check if question is legal domain related"""
        try:
            # Format the prompt
            prompt = self.domain_filter_template.format(question=question)
            
            # Call Groq API for domain filtering
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a domain classification assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "LEGAL"
            
        except Exception as e:
            # If filtering fails, default to allowing the question
            print(f"Domain filtering error: {e}")
            return True

    def get_legal_response(self, question: str) -> str:
        """Get response for legal questions"""
        try:
            # Format chat history for context
            history_text = ""
            if self.chat_history:
                history_text = "\n".join([
                    f"User: {item['question']}\nAssistant: {item['answer'][:200]}..."
                    for item in self.chat_history[-3:]  # Last 3 exchanges for context
                ])
            
            # Format the prompt
            prompt = self.legal_chat_template.format(
                chat_history=history_text,
                question=question
            )
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert legal AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Slightly higher for more natural conversation
                max_tokens=1024
            )
            
            # Clean the AI response before returning
            cleaned_response = self.clean_ai_response(response.choices[0].message.content)
            return cleaned_response
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error getting legal response: {error_msg}")
            raise Exception(f"Error getting legal response: {error_msg}")

    def chat(self, question: str) -> Dict[str, Any]:
        """Main chat function with legal domain filtering"""
        try:
            # Clean and validate input
            question = question.strip()
            if not question:
                return {
                    "success": False,
                    "error": "Please provide a question.",
                    "response": None,
                    "is_legal": False
                }
            
            # Check if question is legal domain related
            is_legal = self.is_legal_question(question)
            
            if not is_legal:
                return {
                    "success": True,
                    "response": "I'm a specialized legal AI assistant focused on judicial and legal matters. Please ask questions related to law, legal procedures, court systems, or legal concepts. I can help with understanding legal terminology, court processes, types of law, legal rights, and similar topics.",
                    "is_legal": False,
                    "domain_filtered": True
                }
            
            # Get legal response
            response = self.get_legal_response(question)
            
            # Add to chat history
            self.chat_history.append({
                "question": question,
                "answer": response,
                "timestamp": None  # Could add timestamp if needed
            })
            
            # Keep only last 10 exchanges to manage memory
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return {
                "success": True,
                "response": response,
                "is_legal": True,
                "domain_filtered": False
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Legal chatbot error: {error_msg}")
            return {
                "success": False,
                "error": f"I apologize, but I'm currently experiencing technical difficulties: {error_msg}. Please try again in a moment.",
                "response": None,
                "is_legal": False
            }

    def clear_history(self):
        """Clear chat history"""
        self.chat_history.clear()
        return {"success": True, "message": "Chat history cleared"}

    def get_chat_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics"""
        return {
            "chat_history_length": len(self.chat_history),
                        "model_used": self.model_name,
            "domain_filtering": True,
            "specialization": "Legal and Judicial Systems"
        }

# Global chatbot instance
legal_chatbot = None

def get_legal_chatbot():
    """Get or create the global legal chatbot instance"""
    global legal_chatbot
    if legal_chatbot is None:
        legal_chatbot = LegalChatbotAgent()
    return legal_chatbot
