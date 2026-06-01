import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Upload, FileText, Trash2, MessageSquare, Clock,
  CheckCircle, XCircle, Loader2, AlertCircle, RefreshCw, Plus, ChevronRight
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { docsApi } from '../config/apiClient';

const STATUS_POLL_MS = 3000;

const statusConfig = {
  pending:    { icon: Clock,         color: 'text-amber-500',  bg: 'bg-amber-50',  border: 'border-amber-200', label: 'Pending'    },
  processing: { icon: Loader2,       color: 'text-blue-500',   bg: 'bg-blue-50',   border: 'border-blue-200',  label: 'Processing' },
  completed:  { icon: CheckCircle,   color: 'text-green-600',  bg: 'bg-green-50',  border: 'border-green-200', label: 'Completed'  },
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

function DropZone({ onFile, uploading }) {
  const inputRef = useRef();
  const [dragging, setDragging] = useState(false);

  const handle = (file) => {
    if (!file || !file.name.toLowerCase().endsWith('.pdf')) return;
    onFile(file);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handle(e.dataTransfer.files[0]);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => !uploading && inputRef.current?.click()}
      className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer
        transition-all duration-200 select-none
        ${dragging ? 'border-gray-900 bg-gray-900/5 scale-[1.01]' : 'border-gray-200 hover:border-gray-400 hover:bg-white/60'}
        ${uploading ? 'cursor-not-allowed opacity-60' : ''}`}
    >
      <input ref={inputRef} type="file" accept=".pdf" className="hidden"
        onChange={(e) => handle(e.target.files[0])} disabled={uploading} />
      <div className="w-12 h-12 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        {uploading
          ? <Loader2 className="h-6 w-6 text-gray-400 animate-spin" />
          : <Upload className="h-6 w-6 text-gray-400" />}
      </div>
      <p className="text-sm font-medium text-gray-700 mb-1">
        {uploading ? 'Uploading…' : 'Drop your PDF here, or click to browse'}
      </p>
      <p className="text-xs text-gray-400">Only PDF files · Max 50 MB</p>
    </div>
  );
}

export default function DocumentsPage() {
  const { token } = useAuth();
  const navigate  = useNavigate();

  const [sessions, setSessions]   = useState([]);
  const [listLoading, setListLoading] = useState(true);
  const [uploadErr, setUploadErr]  = useState('');
  const [uploading, setUploading]  = useState(false);
  const [deleteId, setDeleteId]    = useState(null);
  const pollingRef = useRef({});

  // ── Fetch session list ─────────────────────────────────────────────────────
  const fetchList = useCallback(async () => {
    try {
      const data = await docsApi.listAll(token);
      setSessions(data.sessions ?? []);
    } catch (e) {
      console.error('Failed to load sessions', e);
    } finally {
      setListLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchList(); }, [fetchList]);

  // ── Poll pending/processing sessions ──────────────────────────────────────
  useEffect(() => {
    const needsPoll = sessions.filter(
      (s) => s.processing_status === 'pending' || s.processing_status === 'processing'
    );

    needsPoll.forEach((s) => {
      const id = s.session_id;
      if (pollingRef.current[id]) return; // already polling

      pollingRef.current[id] = setInterval(async () => {
        try {
          const updated = await docsApi.getStatus(id, token);
          setSessions((prev) =>
            prev.map((p) => p.session_id === id ? { ...p, processing_status: updated.processing_status } : p)
          );
          if (updated.processing_status === 'completed' || updated.processing_status === 'failed') {
            clearInterval(pollingRef.current[id]);
            delete pollingRef.current[id];
          }
        } catch { /* ignore polling errors */ }
      }, STATUS_POLL_MS);
    });

    // Cleanup intervals for sessions no longer in need
    return () => {
      Object.keys(pollingRef.current).forEach((id) => {
        if (!needsPoll.find((s) => s.session_id === id)) {
          clearInterval(pollingRef.current[id]);
          delete pollingRef.current[id];
        }
      });
    };
  }, [sessions, token]);

  // Cleanup all on unmount
  useEffect(() => () => {
    Object.values(pollingRef.current).forEach(clearInterval);
  }, []);

  // ── Upload handler ─────────────────────────────────────────────────────────
  const handleUpload = async (file) => {
    setUploadErr('');
    setUploading(true);
    try {
      const newSession = await docsApi.upload(file, token);
      setSessions((prev) => [
        {
          session_id: newSession.session_id,
          document_name: newSession.document_name,
          processing_status: newSession.processing_status,
          created_at: newSession.created_at,
        },
        ...prev,
      ]);
    } catch (err) {
      setUploadErr(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  // ── Delete handler ─────────────────────────────────────────────────────────
  const handleDelete = async (id) => {
    setDeleteId(id);
    try {
      await docsApi.deleteSession(id, token);
      setSessions((prev) => prev.filter((s) => s.session_id !== id));
      clearInterval(pollingRef.current[id]);
      delete pollingRef.current[id];
    } catch (err) {
      alert(err.message);
    } finally {
      setDeleteId(null);
    }
  };

  const fmtDate = (iso) =>
    new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EAEAE4' }}>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">My Documents</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Upload a PDF to start an AI-powered analysis session.
            </p>
          </div>
          <button onClick={fetchList}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors px-3 py-1.5 rounded-lg hover:bg-white/60">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
        </div>

        {/* Drop zone */}
        <div className="mb-4">
          <DropZone onFile={handleUpload} uploading={uploading} />
          {uploadErr && (
            <div className="flex items-center gap-2 text-red-600 text-sm mt-3">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {uploadErr}
            </div>
          )}
        </div>

        {/* Sessions list */}
        <div className="mt-8">
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">
            Sessions · {sessions.length}
          </h2>

          {listLoading ? (
            <div className="flex items-center justify-center py-16 text-gray-400">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              Loading…
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-16 bg-white/40 rounded-2xl border border-gray-200/60">
              <FileText className="h-10 w-10 text-gray-300 mx-auto mb-3" />
              <p className="text-sm text-gray-500">No documents yet. Upload your first PDF above.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((s) => (
                <div key={s.session_id}
                  className="group flex items-center gap-4 bg-white/70 hover:bg-white border border-gray-200/60
                    rounded-2xl px-5 py-4 transition-all duration-150 shadow-sm hover:shadow-md">

                  {/* Icon */}
                  <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-100
                    flex items-center justify-center shrink-0">
                    <FileText className="h-5 w-5 text-amber-600" />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{s.document_name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{fmtDate(s.created_at)}</p>
                  </div>

                  {/* Status */}
                  <StatusBadge status={s.processing_status} />

                  {/* Actions */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {s.processing_status === 'completed' && (
                      <button onClick={() => navigate(`/chat/${s.session_id}`)}
                        className="flex items-center gap-1 text-xs font-medium text-gray-700
                          hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition-colors">
                        <MessageSquare className="h-3.5 w-3.5" />
                        Chat
                      </button>
                    )}
                    <button onClick={() => handleDelete(s.session_id)} disabled={deleteId === s.session_id}
                      className="p-1.5 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-colors">
                      {deleteId === s.session_id
                        ? <Loader2 className="h-4 w-4 animate-spin" />
                        : <Trash2 className="h-4 w-4" />}
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
    </div>
  );
}
