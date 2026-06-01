import React, { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getApiUrl, getPdfUrl } from '../config/api';
import { useAuth } from '../context/AuthContext';
import { docsApi } from '../config/apiClient';
import {
  Upload, FileText, Shield, CheckCircle, Loader2, AlertCircle,
  Search, MessageCircle, Download, Eye, Lock, Database, Brain,
  Trash2, X, ArrowDown, RefreshCw, MessageSquare, Clock,
  CheckCircle2, XCircle, ChevronRight, Save,
} from 'lucide-react';

// ─── Status badge (for saved sessions) ───────────────────────────────────────
const STATUS_POLL_MS = 3000;
const statusConfig = {
  pending:    { icon: Clock,         color: 'text-amber-500',  bg: 'bg-amber-50',  border: 'border-amber-200', label: 'Pending'    },
  processing: { icon: Loader2,       color: 'text-blue-500',   bg: 'bg-blue-50',   border: 'border-blue-200',  label: 'Processing' },
  completed:  { icon: CheckCircle2,  color: 'text-green-600',  bg: 'bg-green-50',  border: 'border-green-200', label: 'Completed'  },
  failed:     { icon: XCircle,       color: 'text-red-500',    bg: 'bg-red-50',    border: 'border-red-200',   label: 'Failed'     },
};

function StatusBadge({ status }) {
  const cfg = statusConfig[status] ?? statusConfig.pending;
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border
      ${cfg.color} ${cfg.bg} ${cfg.border}`}>
      <Icon className={`h-3 w-3 ${status === 'processing' ? 'animate-spin' : ''}`} />
      {cfg.label}
    </span>
  );
}

// ─── Mode Toggle ─────────────────────────────────────────────────────────────
function ModeToggle({ mode, onChange }) {
  return (
    <div className="inline-flex bg-gray-100 rounded-2xl p-1 gap-1">
      <button
        onClick={() => onChange('private')}
        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
          mode === 'private'
            ? 'bg-gray-900 text-white shadow-sm'
            : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        <Lock className="h-3.5 w-3.5" />
        Private · Ephemeral
      </button>
      <button
        onClick={() => onChange('saved')}
        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
          mode === 'saved'
            ? 'bg-gray-900 text-white shadow-sm'
            : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        <Save className="h-3.5 w-3.5" />
        Save to Account
      </button>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// PRIVATE MODE — ephemeral, no DB
// ═══════════════════════════════════════════════════════════════════════════════
function PrivateMode() {
  const fileInputRef = useRef(null);
  const SESSION_KEY  = 'confidential_upload_state';

  const restoreSession = () => {
    try { const s = sessionStorage.getItem(SESSION_KEY); if (s) return JSON.parse(s); } catch {}
    return null;
  };
  const saved = restoreSession();

  const [uploadedFile,     setUploadedFile]     = useState(saved?.uploadedFile || null);
  const [uploading,        setUploading]         = useState(false);
  const [retrieving,       setRetrieving]        = useState(false);
  const [analyzing,        setAnalyzing]         = useState(false);
  const [similarCases,     setSimilarCases]      = useState(saved?.similarCases || []);
  const [analysis,         setAnalysis]          = useState(saved?.analysis || null);
  const [question,         setQuestion]          = useState('');
  const [answer,           setAnswer]            = useState(saved?.answer || '');
  const [isAsking,         setIsAsking]          = useState(false);
  const [hasTriedRetrieve, setHasTriedRetrieve]  = useState(saved?.hasTriedRetrieve || false);
  const [showToast,        setShowToast]         = useState(false);

  const clearSession = () => {
    sessionStorage.removeItem(SESSION_KEY);
    setUploadedFile(null); setSimilarCases([]); setAnalysis(null);
    setAnswer(''); setQuestion(''); setHasTriedRetrieve(false); setShowToast(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  useEffect(() => {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify({ uploadedFile, similarCases, analysis, answer, hasTriedRetrieve }));
    } catch {}
  }, [uploadedFile, similarCases, analysis, answer, hasTriedRetrieve]);

  const uploadFile = async (file) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('is_confidential', 'true');
      const response = await axios.post(getApiUrl('/api/documents'), formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      // v1 returns { document_id, status: 'completed' } for ephemeral uploads
      if (response.data.document_id || response.data.status === 'completed') {
        sessionStorage.removeItem(SESSION_KEY);
        setUploadedFile({ name: file.name, size: file.size });
        setSimilarCases([]); setAnalysis(null); setAnswer(''); setQuestion(''); setHasTriedRetrieve(false);
      } else { alert('Upload failed. Please try again.'); }
    } catch (err) {
      alert(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally { setUploading(false); }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.type !== 'application/pdf') { alert('PDF files only.'); return; }
    if (file.size > 10 * 1024 * 1024) { alert('Max 10 MB.'); return; }
    uploadFile(file);
  };

  const retrieveSimilarCases = async () => {
    if (!uploadedFile) return;
    try {
      setRetrieving(true); setHasTriedRetrieve(true);
      const response = await axios.get(
        getApiUrl(`/api/documents/${encodeURIComponent(uploadedFile.name)}/similar-cases?top_k=5`)
      );
      setSimilarCases(response.data.similar_cases || []);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to retrieve similar cases.');
    } finally { setRetrieving(false); }
  };

  const analyzeDocument = async () => {
    if (!uploadedFile) return;
    try {
      setAnalyzing(true);
      const response = await axios.get(
        getApiUrl(`/api/documents/${encodeURIComponent(uploadedFile.name)}/analysis`)
      );
      const summary = response.data.analysis?.summary || response.data.summary || 'Analysis completed.';
      setAnalysis(summary);
      setShowToast(true); setTimeout(() => setShowToast(false), 5000);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to analyze document.');
    } finally { setAnalyzing(false); }
  };

  const askQuestion = async () => {
    if (!question.trim() || !uploadedFile) return;
    try {
      setIsAsking(true);
      const response = await axios.post(
        getApiUrl(`/api/documents/${encodeURIComponent(uploadedFile.name)}/chat`),
        { question: question.trim() }
      );
      const answer = response.data.message || response.data.answer || 'No answer returned.';
      setAnswer(answer);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to process question.');
    } finally { setIsAsking(false); }
  };

  const formatSize = (b) => {
    const k = 1024, s = ['Bytes','KB','MB','GB'], i = Math.floor(Math.log(b) / Math.log(k));
    return `${parseFloat((b / Math.pow(k, i)).toFixed(2))} ${s[i]}`;
  };

  const navigate = useNavigate();

  return (
    <div className="space-y-4">
      {/* Toast */}
      {showToast && (
        <div className="fixed bottom-5 left-4 right-4 sm:left-1/2 sm:right-auto sm:-translate-x-1/2 z-50 flex items-center gap-2.5 bg-gray-900 text-white text-xs sm:text-sm font-medium px-4 py-2.5 rounded-2xl shadow-lg max-w-sm mx-auto sm:mx-0 sm:w-max">
          <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
          <span className="flex-1">Summary ready — scroll down to view</span>
          <ArrowDown className="h-3.5 w-3.5 text-gray-400" />
          <button onClick={() => setShowToast(false)} className="ml-1 text-gray-400 hover:text-white"><X className="h-3.5 w-3.5" /></button>
        </div>
      )}

      {/* Privacy notice */}
      <div className="bg-white/70 rounded-2xl border border-gray-200/60 p-5">
        <div className="flex items-start gap-3">
          <div className="bg-gray-100 p-2 rounded-lg flex-shrink-0 mt-0.5"><Shield className="h-4 w-4 text-gray-600" /></div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-1">Private &amp; Ephemeral</h3>
            <p className="text-xs text-gray-500 leading-relaxed">Your file is processed in memory only. Nothing is stored in any database or linked to your account — this session disappears when you leave the page or click Delete Session.</p>
          </div>
        </div>
      </div>

      {/* Upload card */}
      <div className="bg-white rounded-2xl border border-gray-200/60">
        <div className="p-5 sm:p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <Upload className="h-4 w-4 text-gray-600" /> Upload Document
            </h2>
            {uploadedFile && (
              <button onClick={clearSession} className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 border border-red-200 text-red-600 rounded-full text-xs font-medium transition-colors">
                <Trash2 className="h-3.5 w-3.5" /><span>Delete Session</span>
              </button>
            )}
          </div>

          {!uploadedFile ? (
            <div
              className="border-2 border-dashed border-gray-200 rounded-xl p-10 text-center hover:border-gray-300 transition-colors cursor-pointer"
              onClick={() => !uploading && fileInputRef.current?.click()}
            >
              <input type="file" ref={fileInputRef} onChange={handleFileSelect} accept=".pdf" className="hidden" />
              <div className="bg-gray-900 w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4">
                {uploading ? <Loader2 className="h-7 w-7 text-white animate-spin" /> : <FileText className="h-7 w-7 text-white" />}
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">{uploading ? 'Uploading…' : 'Drop your PDF here or click to browse'}</h3>
              <p className="text-xs text-gray-500">Maximum 10 MB · PDF files only</p>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 flex items-center gap-3">
              <div className="bg-gray-900 p-2.5 rounded-lg flex-shrink-0"><CheckCircle className="h-5 w-5 text-white" /></div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">{uploadedFile.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{formatSize(uploadedFile.size)} · Uploaded successfully</p>
              </div>
              <button onClick={clearSession} className="text-gray-400 hover:text-gray-600 p-1.5 hover:bg-gray-200 rounded-lg transition-colors">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Analysis options */}
      {uploadedFile && (
        <div className="bg-white rounded-2xl border border-gray-200/60 p-5 sm:p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-5 flex items-center gap-2">
            <Brain className="h-4 w-4 text-gray-600" /> Analysis Options
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-gray-50 border border-gray-100 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2"><Search className="h-4 w-4 text-gray-600" /><h3 className="text-sm font-semibold text-gray-900">Find Similar Cases</h3></div>
              <p className="text-xs text-gray-500 mb-4 leading-relaxed">Search our database for cases similar to your uploaded document.</p>
              <button onClick={retrieveSimilarCases} disabled={retrieving} className="w-full bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white py-2.5 rounded-full text-sm font-medium transition-colors flex items-center justify-center gap-2">
                {retrieving ? <><Loader2 className="h-4 w-4 animate-spin" /><span>Searching…</span></> : <><Search className="h-4 w-4" /><span>Find Similar Cases</span></>}
              </button>
            </div>
            <div className="bg-gray-50 border border-gray-100 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-2"><MessageCircle className="h-4 w-4 text-gray-600" /><h3 className="text-sm font-semibold text-gray-900">Analyze &amp; Chat</h3></div>
              <p className="text-xs text-gray-500 mb-4 leading-relaxed">Get an AI-powered summary and ask specific questions about this document.</p>
              <button onClick={analyzeDocument} disabled={analyzing} className="w-full bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white py-2.5 rounded-full text-sm font-medium transition-colors flex items-center justify-center gap-2">
                {analyzing ? <><Loader2 className="h-4 w-4 animate-spin" /><span>Analyzing…</span></> : <><MessageCircle className="h-4 w-4" /><span>Summarize &amp; Q&amp;A</span></>}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Similar cases */}
      {similarCases.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200/60 p-5 sm:p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-5 flex items-center gap-2">
            <Database className="h-4 w-4 text-gray-600" /> Similar Cases Found ({similarCases.length})
          </h2>
          <div className="space-y-3">
            {similarCases.map((c, i) => (
              <div key={i} className="border border-gray-200/60 rounded-xl p-4 sm:p-5 hover:border-gray-300 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <FileText className="h-4 w-4 text-gray-500 flex-shrink-0" />
                    <h3 className="text-sm font-semibold text-gray-900 truncate">
                      {c.title || (c.filename || c.name || 'Unknown').replace(/\.pdf$/i,'').replace(/__+/g,' — ').replace(/[_]+/g,' ').trim()}
                    </h3>
                  </div>
                  <span className="self-start sm:self-auto px-2.5 py-1 bg-gray-100 text-gray-600 text-xs rounded-full font-medium whitespace-nowrap">
                    {((c.score || c.similarity || 0) * 100).toFixed(1)}% match
                  </span>
                </div>
                <p className="text-xs text-gray-500 leading-relaxed mb-4 line-clamp-2">{c.content || c.text || 'Legal case document available for analysis.'}</p>
                <div className="flex flex-wrap gap-2">
                  <button onClick={() => navigate(`/analyze/${encodeURIComponent(c.filename || c.name || '')}`, { state: { from: '/analysis' } })}
                    className="flex items-center gap-1.5 px-4 py-2 bg-gray-900 hover:bg-gray-700 text-white rounded-full text-xs font-medium transition-colors">
                    <Brain className="h-3.5 w-3.5" /><span>Analyze</span>
                  </button>
                  <button onClick={() => window.open(getPdfUrl(c.filename || c.name || ''), '_blank')}
                    className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 hover:border-gray-300 text-gray-700 rounded-full text-xs font-medium transition-colors">
                    <Eye className="h-3.5 w-3.5" /><span>View</span>
                  </button>
                  <a href={getPdfUrl(c.filename || c.name || '')} download
                    className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 hover:border-gray-300 text-gray-700 rounded-full text-xs font-medium transition-colors">
                    <Download className="h-3.5 w-3.5" /><span>Download</span>
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No results */}
      {!retrieving && hasTriedRetrieve && similarCases.length === 0 && uploadedFile && (
        <div className="bg-white rounded-2xl border border-gray-200/60 p-8 text-center">
          <div className="bg-gray-100 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"><Search className="h-5 w-5 text-gray-500" /></div>
          <h3 className="text-sm font-semibold text-gray-900 mb-1">No Similar Cases Found</h3>
          <p className="text-xs text-gray-500 mb-4">We couldn't find similar cases for your document.</p>
          <button onClick={retrieveSimilarCases} className="bg-gray-900 hover:bg-gray-700 text-white px-5 py-2 rounded-full text-sm font-medium transition-colors">Try Again</button>
        </div>
      )}

      {/* Analysis result + Q&A */}
      {analysis && (
        <div className="bg-white rounded-2xl border border-gray-200/60 p-5 sm:p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2"><Brain className="h-4 w-4 text-gray-600" /> Document Analysis</h2>
          <div className="bg-gray-50 border border-gray-100 rounded-xl p-5 mb-5">
            <div className="prose prose-sm max-w-none text-gray-700 prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-strong:font-semibold">
              <ReactMarkdown>{analysis}</ReactMarkdown>
            </div>
          </div>
          <div className="border-t border-gray-100 pt-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2"><MessageCircle className="h-4 w-4 text-gray-600" /> Ask Questions</h3>
            <div className="flex gap-2 mb-3">
              <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); askQuestion(); } }}
                placeholder="Ask a specific question about this document…"
                className="flex-1 px-4 py-2.5 text-sm border border-gray-200 rounded-xl bg-gray-50 focus:ring-2 focus:ring-gray-900/10 focus:border-gray-300 outline-none transition-all" disabled={isAsking} />
              <button onClick={askQuestion} disabled={!question.trim() || isAsking}
                className="bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap">
                {isAsking ? <><Loader2 className="h-4 w-4 animate-spin" /><span>Asking…</span></> : <><MessageCircle className="h-4 w-4" /><span>Ask</span></>}
              </button>
            </div>
            {answer && (
              <div className="bg-gray-50 border border-gray-100 rounded-xl p-5">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Answer</h4>
                <div className="prose prose-sm max-w-none text-gray-800 prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-strong:font-semibold">
                  <ReactMarkdown>{answer}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SAVED MODE — persistent, stored to PostgreSQL
// ═══════════════════════════════════════════════════════════════════════════════
function SavedMode() {
  const { token } = useAuth();
  const navigate  = useNavigate();

  const [sessions,     setSessions]     = useState([]);
  const [listLoading,  setListLoading]  = useState(true);
  const [uploadErr,    setUploadErr]    = useState('');
  const [uploading,    setUploading]    = useState(false);
  const [deleteId,     setDeleteId]     = useState(null);
  const [dragging,     setDragging]     = useState(false);
  const inputRef = useRef();
  const pollingRef = useRef({});

  const fetchList = useCallback(async () => {
    try {
      const data = await docsApi.listAll(token);
      setSessions(data.sessions ?? []);
    } catch (e) { console.error('Failed to load sessions', e); }
    finally { setListLoading(false); }
  }, [token]);

  useEffect(() => { fetchList(); }, [fetchList]);

  // Poll pending/processing sessions
  useEffect(() => {
    const needsPoll = sessions.filter((s) => s.processing_status === 'pending' || s.processing_status === 'processing');
    needsPoll.forEach((s) => {
      const id = s.session_id;
      if (pollingRef.current[id]) return;
      pollingRef.current[id] = setInterval(async () => {
        try {
          const updated = await docsApi.getStatus(id, token);
          setSessions((prev) => prev.map((p) => p.session_id === id ? { ...p, processing_status: updated.processing_status } : p));
          if (updated.processing_status === 'completed' || updated.processing_status === 'failed') {
            clearInterval(pollingRef.current[id]); delete pollingRef.current[id];
          }
        } catch {}
      }, STATUS_POLL_MS);
    });
    return () => {
      Object.keys(pollingRef.current).forEach((id) => {
        if (!needsPoll.find((s) => s.session_id === id)) { clearInterval(pollingRef.current[id]); delete pollingRef.current[id]; }
      });
    };
  }, [sessions, token]);

  useEffect(() => () => { Object.values(pollingRef.current).forEach(clearInterval); }, []);

  const handleFile = (file) => {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) return;
    handleUpload(file);
  };

  const handleUpload = async (file) => {
    setUploadErr(''); setUploading(true);
    try {
      const newSession = await docsApi.upload(file, token);
      setSessions((prev) => [{
        session_id: newSession.session_id,
        document_name: newSession.document_name,
        processing_status: newSession.processing_status,
        created_at: newSession.created_at,
      }, ...prev]);
    } catch (err) { setUploadErr(err.message || 'Upload failed. Please try again.'); }
    finally { setUploading(false); }
  };

  const handleDelete = async (id) => {
    setDeleteId(id);
    try {
      await docsApi.deleteSession(id, token);
      setSessions((prev) => prev.filter((s) => s.session_id !== id));
      clearInterval(pollingRef.current[id]); delete pollingRef.current[id];
    } catch (err) { alert(err.message); }
    finally { setDeleteId(null); }
  };

  const fmtDate = (iso) => new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

  return (
    <div className="space-y-4">
      {/* Info notice */}
      <div className="bg-white/70 rounded-2xl border border-gray-200/60 p-5">
        <div className="flex items-start gap-3">
          <div className="bg-gray-100 p-2 rounded-lg flex-shrink-0 mt-0.5"><Database className="h-4 w-4 text-gray-600" /></div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-1">Saved to Your Account</h3>
            <p className="text-xs text-gray-500 leading-relaxed">Documents uploaded here are stored in your account's secure workspace. Sessions persist across devices and are linked only to your login.</p>
          </div>
        </div>
      </div>

      {/* Drop zone */}
      <div className="bg-white rounded-2xl border border-gray-200/60 p-5 sm:p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2"><Upload className="h-4 w-4 text-gray-600" /> Upload &amp; Save</h2>
          <button onClick={fetchList} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-100">
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
        </div>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
          onClick={() => !uploading && inputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 select-none
            ${dragging ? 'border-gray-900 bg-gray-900/5 scale-[1.01]' : 'border-gray-200 hover:border-gray-400 hover:bg-white/60'}
            ${uploading ? 'cursor-not-allowed opacity-60' : ''}`}
        >
          <input ref={inputRef} type="file" accept=".pdf" className="hidden"
            onChange={(e) => handleFile(e.target.files[0])} disabled={uploading} />
          <div className="w-12 h-12 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            {uploading ? <Loader2 className="h-6 w-6 text-gray-400 animate-spin" /> : <Upload className="h-6 w-6 text-gray-400" />}
          </div>
          <p className="text-sm font-medium text-gray-700 mb-1">{uploading ? 'Uploading…' : 'Drop your PDF here, or click to browse'}</p>
          <p className="text-xs text-gray-400">Only PDF files · Max 50 MB</p>
        </div>
        {uploadErr && (
          <div className="flex items-center gap-2 text-red-600 text-sm mt-3"><AlertCircle className="h-4 w-4 shrink-0" />{uploadErr}</div>
        )}
      </div>

      {/* Sessions list */}
      <div>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3 px-1">
          Sessions · {sessions.length}
        </h2>
        {listLoading ? (
          <div className="flex items-center justify-center py-16 text-gray-400">
            <Loader2 className="h-6 w-6 animate-spin mr-2" /> Loading…
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-16 bg-white/40 rounded-2xl border border-gray-200/60">
            <FileText className="h-10 w-10 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-500">No saved documents yet. Upload your first PDF above.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {sessions.map((s) => (
              <div key={s.session_id}
                className="group flex items-center gap-4 bg-white/70 hover:bg-white border border-gray-200/60
                  rounded-2xl px-5 py-4 transition-all duration-150 shadow-sm hover:shadow-md">
                <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center shrink-0">
                  <FileText className="h-5 w-5 text-amber-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{s.document_name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{fmtDate(s.created_at)}</p>
                </div>
                <StatusBadge status={s.processing_status} />
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {s.processing_status === 'completed' && (
                    <button onClick={() => navigate(`/chat/${s.session_id}`)}
                      className="flex items-center gap-1 text-xs font-medium text-gray-700 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition-colors">
                      <MessageSquare className="h-3.5 w-3.5" /> Chat
                    </button>
                  )}
                  <button onClick={() => handleDelete(s.session_id)} disabled={deleteId === s.session_id}
                    className="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors">
                    {deleteId === s.session_id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                  </button>
                </div>
                {s.processing_status === 'completed' && (
                  <ChevronRight className="h-4 w-4 text-gray-300 group-hover:text-gray-500 transition-colors cursor-pointer"
                    onClick={() => navigate(`/chat/${s.session_id}`)} />
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// ROOT — merged shell with mode toggle
// ═══════════════════════════════════════════════════════════════════════════════
export default function AnalysisPage() {
  const [mode, setMode] = useState('private');

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EAEAE4' }}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight mb-1">Case Analysis</h1>
          <p className="text-sm text-gray-500">
            {mode === 'private'
              ? 'Analyse a confidential document without leaving any trace.'
              : 'Upload documents to your personal workspace and revisit them any time.'}
          </p>
        </div>

        {/* Mode toggle */}
        <div className="mb-8">
          <ModeToggle mode={mode} onChange={setMode} />
        </div>

        {/* Content */}
        {mode === 'private' ? <PrivateMode /> : <SavedMode />}
      </div>
    </div>
  );
}
