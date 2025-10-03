// API Configuration
const API_CONFIG = {
  // Use environment variable if available, otherwise fallback to production URL
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://13.71.23.132',
  
  // API endpoints
  ENDPOINTS: {
    SEARCH: '/api/search',
    HEALTH: '/api/health',
    LEGAL_CHAT: '/api/legal-chat',
    LEGAL_CHAT_STATS: '/api/legal-chat/stats',
    UPLOAD_CONFIDENTIAL: '/api/upload-confidential-pdf',
    RETRIEVE_SIMILAR_CASES: '/api/retrieve-similar-cases',
    ANALYZE_CONFIDENTIAL: '/api/analyze-confidential-pdf',
    ASK_QUESTION_CONFIDENTIAL: '/api/ask-question-confidential',
    ANALYZE_DOCUMENT: '/api/analyze-document',
    DOCUMENT_STATS: '/api/document-stats',
    ASK_QUESTION: '/api/ask-question',
    PDF: '/api/pdf',
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