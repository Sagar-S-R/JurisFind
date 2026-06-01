/**
 * Centralised API client for JurisFind
 * All requests target /api/* business-capability routes.
 * Automatically injects Authorization: Bearer <token> on authenticated calls.
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '';

async function request(path, options = {}, token = null) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers ?? {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  // Parse body regardless of status so we can return error detail
  let body;
  const ct = res.headers.get('content-type') ?? '';
  if (ct.includes('application/json')) {
    body = await res.json();
  } else {
    body = await res.text();
  }

  if (!res.ok) {
    const msg = body?.detail ?? body ?? `HTTP ${res.status}`;
    const err = new Error(typeof msg === 'object' ? JSON.stringify(msg) : msg);
    err.status = res.status;
    throw err;
  }
  return body;
}

// ── Auth ─── /api/auth/* ───────────────────────────────────────────────────
export const authApi = {
  register: (email, password) =>
    request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  login: (email, password) =>
    request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
};

// ── Cases ─── /api/cases/* ────────────────────────────────────────────────
export const casesApi = {
  search: (query, top_k = 10) =>
    request('/api/cases/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k }),
    }),

  get: (caseId) =>
    request(`/api/cases/${encodeURIComponent(caseId)}`),
};

// ── Documents ─── /api/documents/* ────────────────────────────────────────
export const docsApi = {
  // Persistent file upload (multipart, is_confidential=false)
  upload: (file, token) => {
    const form = new FormData();
    form.append('file', file);
    form.append('is_confidential', 'false');
    return fetch(`${BASE}/api/documents`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    }).then(async (res) => {
      const body = await res.json();
      if (!res.ok) throw new Error(body?.detail ?? `HTTP ${res.status}`);
      return body;
    });
  },

  // Ephemeral / confidential upload (multipart, is_confidential=true)
  uploadConfidential: (file) => {
    const form = new FormData();
    form.append('file', file);
    form.append('is_confidential', 'true');
    return fetch(`${BASE}/api/documents`, {
      method: 'POST',
      body: form,
    }).then(async (res) => {
      const body = await res.json();
      if (!res.ok) throw new Error(body?.detail ?? `HTTP ${res.status}`);
      return body;
    });
  },

  // Database case ingestion (JSON body)
  retrieve: (caseId, token) =>
    request('/api/documents/retrieve', {
      method: 'POST',
      body: JSON.stringify({ source_type: 'database', case_id: caseId, is_confidential: false }),
    }, token),

  // List all document sessions for current user
  listAll: (token, page = 1, pageSize = 20) =>
    request(`/api/documents?page=${page}&page_size=${pageSize}`, {}, token),

  // Poll processing status
  getStatus: (documentId, token) =>
    request(`/api/documents/${documentId}/status`, {}, token),

  // Unified analysis (summary + stats)
  getAnalysis: (documentId, token = null) =>
    request(`/api/documents/${documentId}/analysis`, {}, token),

  // Find similar cases using an ephemeral document as query
  getSimilarCases: (documentId, topK = 5) =>
    request(`/api/documents/${encodeURIComponent(documentId)}/similar-cases?top_k=${topK}`),

  // Delete session (persistent or ephemeral)
  deleteSession: (documentId, token) =>
    request(`/api/documents/${documentId}`, { method: 'DELETE' }, token),

  // Q&A chat (persistent or ephemeral)
  chat: (documentId, question, token = null) =>
    request(`/api/documents/${encodeURIComponent(documentId)}/chat`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    }, token),

  // Get conversation thread history
  getChatHistory: (documentId, token) =>
    request(`/api/documents/${documentId}/chat`, {}, token),
};

// ── Legal Chatbot ─── /api/chat/legal ─────────────────────────────────────
export const chatApi = {
  // General legal domain chatbot
  legal: (question) =>
    request('/api/chat/legal', {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),

  // Document-scoped chat (alias for docsApi.chat — kept for backward compat)
  ask: (documentId, question, token) =>
    docsApi.chat(documentId, question, token),

  history: (documentId, token) =>
    docsApi.getChatHistory(documentId, token),
};
