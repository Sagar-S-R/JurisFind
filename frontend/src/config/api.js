// API Configuration
const API_CONFIG = {
  // Set VITE_API_BASE_URL in .env.local for local dev (e.g. http://localhost:8000)
  // Leave it empty ("") in Vercel env vars for production — Vercel proxy handles routing
  BASE_URL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    SEARCH: '/api/search',
    HEALTH: '/api/health',
    LEGAL_CHAT: '/api/legal-chat',
    LEGAL_CHAT_STATS: '/api/legal-chat/stats',
    UPLOAD_CONFIDENTIAL: '/api/upload-confidential-pdf',
    RETRIEVE_SIMILAR_CASES: '/api/retrieve-similar-cases',
    // Legacy endpoints (kept for backward compatibility)
    ANALYZE_CONFIDENTIAL: '/api/analyze-confidential-pdf',
    ASK_QUESTION_CONFIDENTIAL: '/api/ask-question-confidential',
    ANALYZE_DOCUMENT: '/api/analyze-document',
    DOCUMENT_STATS: '/api/document-stats',
    ASK_QUESTION: '/api/ask-question',
    PDF: '/api/pdf',
    // Unified endpoints (new)
    UNIFIED_ANALYZE: '/api/unified/analyze',
    UNIFIED_ASK: '/api/unified/ask',
  }
};

// Helper function to get full API URL
export const getApiUrl = (endpoint, params = '') => {
  return `${API_CONFIG.BASE_URL}${endpoint}${params}`;
};

// Helper function to get PDF URL
export const getPdfUrl = (filename) => {
  return `${API_CONFIG.BASE_URL}/api/pdf/${encodeURIComponent(filename)}`;
};

export default API_CONFIG;