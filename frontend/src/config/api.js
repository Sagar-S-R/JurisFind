// API Configuration — v1
const API_CONFIG = {
  // Set VITE_API_BASE_URL=http://localhost:8000 in .env.local for local dev
  // In production (Vercel), leave unset — defaults to '' so Vercel proxy handles routing
  BASE_URL: import.meta.env.VITE_API_BASE_URL ?? '',

  // API endpoints (business-capability oriented)
  ENDPOINTS: {
    // Health
    HEALTH: '/api/health',

    // Authentication
    AUTH_REGISTER: '/api/auth/register',
    AUTH_LOGIN: '/api/auth/login',

    // Cases (search & retrieval)
    CASES_SEARCH: '/api/cases/search',
    CASES_GET: '/api/cases',         // + /{case_id}

    // Documents (unified ingestion, analysis, chat)
    DOCUMENTS: '/api/documents',     // POST (ingest), GET (list)
    DOCUMENT_RETRIEVE: '/api/documents/retrieve',  // POST with JSON body
    // Sub-routes: /api/documents/{id}/status|analysis|chat|similar-cases

    // Legal chatbot
    LEGAL_CHAT: '/api/chat/legal',

    // PDF viewer (served directly)
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