import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation, Link } from 'react-router-dom';
import {
  Send, FileText, Loader2, AlertCircle, Plus,
  User, Bot, BookOpen, Trash2,
  MessageSquare, History, Search,
  Menu, X, Paperclip, Clock
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { chatApi, sessionsApi, docsApi } from '../config/apiClient';

// ── Message Component ──────────────────────────────────────────────────────

function Message({ msg }) {
  const isUser   = msg.role === 'user';
  const isSystem = msg.role === 'system';
  const hasCitations = msg.citations && msg.citations.length > 0;

  // Subtle system/status messages — nonchalant, inline, low-opacity
  if (isSystem) {
    return (
      <div className="flex justify-center my-3">
        <span className="text-[11px] text-gray-400 tracking-wide">{msg.content}</span>
      </div>
    );
  }

  return (
    <div className={`flex items-start gap-3 mb-6 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0
        ${isUser ? 'bg-gray-800' : 'bg-amber-100 border border-amber-200'}`}>
        {isUser
          ? <User className="h-3.5 w-3.5 text-white" />
          : <Bot className="h-3.5 w-3.5 text-amber-700" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
        ${isUser
          ? 'bg-gray-800 text-white rounded-tr-sm'
          : 'bg-white border border-gray-100 text-gray-800 rounded-tl-sm shadow-sm'}`}>

        {/* PDF chip inside user message if present */}
        {isUser && msg.attachedFile && (
          <div className="flex items-center gap-2 mb-2 bg-gray-700 rounded-lg px-2.5 py-1.5">
            <FileText className="h-3.5 w-3.5 text-amber-400 shrink-0" />
            <span className="text-xs text-gray-200 truncate max-w-[200px]">{msg.attachedFile}</span>
            <span className="text-[10px] text-gray-400 ml-auto">PDF</span>
          </div>
        )}

        {msg.content && (
          <p className="whitespace-pre-wrap">{msg.content}</p>
        )}

        {/* Citations */}
        {hasCitations && (
          <div className="mt-4 pt-3 border-t border-gray-100">
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Sources Cited</p>
            <div className="grid grid-cols-1 gap-2">
              {msg.citations.map((cite, idx) => (
                <div key={idx} className="bg-gray-50 border border-gray-200 rounded-xl p-2.5 hover:bg-amber-50/50 hover:border-amber-200 transition-all">
                  <div className="flex items-center gap-2 mb-1">
                    <BookOpen className="h-3.5 w-3.5 text-amber-600 shrink-0" />
                    <span className="text-[11px] font-semibold text-gray-700 truncate">{cite.document_title}</span>
                    <span className="text-[10px] text-gray-400 bg-white px-1.5 py-0.5 rounded border border-gray-100 ml-auto shrink-0">Page {cite.page_number}</span>
                  </div>
                  <p className="text-[11px] text-gray-500 italic line-clamp-2 leading-snug">"{cite.excerpt}..."</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {msg.timestamp && (
          <p className="text-[10px] mt-2 opacity-40 flex items-center gap-1">
            <Clock className="h-2.5 w-2.5" />
            {new Date(msg.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  );
}

// ── Assistant Page ─────────────────────────────────────────────────────────

export default function AssistantPage() {
  const { sessionId } = useParams();
  const navigate      = useNavigate();
  const location      = useLocation();
  const { token }     = useAuth();

  const [sessions, setSessions]           = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [session, setSession]             = useState(null);
  const [messages, setMessages]           = useState([]);
  const [question, setQuestion]           = useState('');
  const [sending, setSending]             = useState(false);
  const [histLoading, setHistLoading]     = useState(false);
  const [error, setError]                 = useState('');
  const [sidebarOpen, setSidebarOpen]     = useState(true);

  // PDF staging — the file is held in state until the user sends a message
  const [stagedFile, setStagedFile]       = useState(null); // { file: File, name: string }
  const [uploading, setUploading]         = useState(false);

  const bottomRef = useRef(null);
  const inputRef  = useRef(null);
  const fileRef   = useRef(null);

  // ── Fetch / Load Helpers ──────────────────────────────────────────────────

  const fetchSessions = useCallback(async () => {
    try {
      const data = await sessionsApi.list(token);
      setSessions(data || []);
    } catch (e) { console.error('Sessions list err', e); }
    finally { setSessionsLoading(false); }
  }, [token]);

  const loadHistory = useCallback(async () => {
    if (!sessionId) { setSession(null); setMessages([]); return; }
    
    // If we just created this session in sendMessage(), don't wipe out the optimistic messages.
    if (location.state?.skipLoad) return;

    setHistLoading(true);
    setMessages([]);
    setError('');
    try {
      const [sess, history] = await Promise.all([
        sessionsApi.get(sessionId, token),
        chatApi.history(sessionId, token)
      ]);
      setSession(sess);

      const loadedMessages = history || [];

      // If navigated here from Analyze (session has a processing doc, no messages yet),
      // show an immediate "reading document..." status so the user isn't looking at a blank screen
      const hasProcessingDoc = sess.documents?.some(
        d => d.status === 'processing' || d.status === 'uploaded'
      );
      if (hasProcessingDoc && loadedMessages.length === 0) {
        setMessages([{
          role: 'system',
          content: 'reading document...',
          timestamp: new Date().toISOString()
        }]);
      } else {
        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error('Session load err', err);
      setError('Could not load session.');
    } finally {
      setHistLoading(false);
    }
  }, [sessionId, token]);


  useEffect(() => { fetchSessions(); }, [fetchSessions]);
  useEffect(() => { loadHistory(); }, [loadHistory, location.state]);

  // ── Poll for processing status ────────────────────────────────────────────
  useEffect(() => {
    if (!sessionId || !session) return;
    const processingDocs = session.documents?.filter(d =>
      d.status === 'processing' || d.status === 'uploaded'
    ) || [];
    if (processingDocs.length === 0) return;

    const timer = setInterval(async () => {
      try {
        const updatedSess = await sessionsApi.get(sessionId, token);
        const wasProcessing = session.documents?.some(d => d.status === 'processing' || d.status === 'uploaded');
        const isNowReady = updatedSess.documents?.every(d => d.status === 'ready');
        setSession(updatedSess);
        if (wasProcessing && isNowReady) {
          // Nonchalant — no emoji, lowercase, subtle
          setMessages(prev => [...prev, {
            role: 'system',
            content: 'ready.',
            timestamp: new Date().toISOString()
          }]);
          fetchSessions();
        }
      } catch (e) {}
    }, 3000);

    return () => clearInterval(timer);
  }, [sessionId, session, token, fetchSessions]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]); // only scroll when a new message is added, not on content/citation mutations


  // ── Action Handlers ───────────────────────────────────────────────────────

  // ─ New chat: just navigate to /assistant (no session created yet)
  // The session is created lazily on the first message — like Claude/ChatGPT
  const createNewChat = () => {
    if (!sessionId) return;           // already on a blank page
    setStagedFile(null);
    setQuestion('');
    navigate('/assistant');
  };

  const deleteSession = async (e, id) => {
    e.stopPropagation();
    // Optimistic remove — instant UI response
    setSessions(prev => prev.filter(s => s.id !== id));
    if (sessionId === id) navigate('/assistant');
    try {
      await sessionsApi.delete(id, token);
    } catch (err) {
      // Revert if server rejected it
      console.error('Delete failed:', err);
      fetchSessions();
    }
  };

  // File is selected → stage it, don't send yet
  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setStagedFile({ file, name: file.name });
    if (fileRef.current) fileRef.current.value = '';
    inputRef.current?.focus();
  };

  const removeStagedFile = () => setStagedFile(null);

  // Upload + attach the staged PDF, return the document ID
  const uploadAndAttach = async (activeId) => {
    if (!stagedFile) return null;
    setUploading(true);
    try {
      const doc = await docsApi.upload(stagedFile.file, token);
      await sessionsApi.attachDocument(activeId, doc.id, token);
      setSession(prev => ({
        ...prev,
        documents: [...(prev?.documents || []), { id: doc.id, title: stagedFile.name, status: 'processing' }]
      }));
      return doc.id;   // caller will poll this
    } catch (err) {
      setError('Upload failed: ' + err.message);
      return null;
    } finally {
      setUploading(false);
      setStagedFile(null);
    }
  };

  // Poll document status until 'ready' or 'failed' (max 90 s)
  const pollUntilReady = async (docId) => {
    const MAX_ATTEMPTS = 30;   // 30 × 3 s = 90 s
    const INTERVAL_MS  = 3000;
    for (let i = 0; i < MAX_ATTEMPTS; i++) {
      await new Promise(r => setTimeout(r, INTERVAL_MS));
      try {
        const status = await docsApi.getStatus(docId, token);
        if (status.status === 'ready')  return true;
        if (status.status === 'failed') return false;
      } catch (e) { /* retry silently */ }
    }
    return false;  // timed out
  };

  const sendMessage = async (e) => {
    e?.preventDefault();
    const q = question.trim();
    if ((!q && !stagedFile) || sending) return;

    // Create session if none
    let activeId = sessionId;
    if (!activeId) {
      try {
        const newSess = await sessionsApi.create('New Session', token);
        activeId = newSess.id;
        setSessions(prev => [newSess, ...prev]);
        navigate(`/assistant/${activeId}`, { replace: true, state: { skipLoad: true } });
        // Give react-router a tick to settle
        await new Promise(r => setTimeout(r, 50));
      } catch (e) { setError('Failed to create session'); return; }
    }

    // Optimistically show the user message (with PDF chip if file staged)
    const attachedFileName = stagedFile?.name || null;
    setQuestion('');
    setError('');

    const userMsg = {
      role: 'user',
      content: q,
      attachedFile: attachedFileName,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);

    // Don't show a text-less message if user only uploaded without text
    setSending(true);

    // Upload file + wait for it to be ready before asking the AI
    if (stagedFile) {
      const docId = await uploadAndAttach(activeId);

      if (docId && q) {
        // Show reading indicator
        setMessages(prev => [...prev, {
          role: 'system',
          content: 'reading document...',
          timestamp: new Date().toISOString()
        }]);

        const ready = await pollUntilReady(docId);

        // Replace "reading" with the final quiet status
        setMessages(prev => {
          const clone = [...prev];
          // find and update the last system message
          for (let i = clone.length - 1; i >= 0; i--) {
            if (clone[i].role === 'system' && clone[i].content === 'reading document...') {
              clone[i] = { ...clone[i], content: ready ? 'saved.' : 'processing took too long — ask anyway.' };
              break;
            }
          }
          return clone;
        });

        if (!ready) {
          // Continue anyway — the AI will say what it can
        }

        // Refresh session to reflect ready state
        sessionsApi.get(activeId, token).then(setSession).catch(() => {});
      }
    }

    // If there's no text question, we're done — just uploaded
    if (!q) {
      setSending(false);
      return;
    }

    // Stream AI response
    const assistantMsgId = 'stream-' + Date.now();
    setMessages(prev => [...prev, {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      citations: [],
      timestamp: new Date().toISOString()
    }]);

    try {
      const response = await chatApi.ask(activeId, q, token);
      if (!response.body) throw new Error('No response body');

      const reader  = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) continue;
          if (line.startsWith('event: citations')) {
            const dataStr = line.replace('event: citations\ndata: ', '').trim();
            try {
              const citations = JSON.parse(dataStr);
              setMessages(prev => prev.map(m => m.id === assistantMsgId ? { ...m, citations } : m));
            } catch (e) {}
          } else if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]') continue;
            try {
              const data = JSON.parse(dataStr);
              if (data.content) {
                setMessages(prev => prev.map(m =>
                  m.id === assistantMsgId ? { ...m, content: m.content + data.content } : m
                ));
              }
            } catch (e) {}
          }
        }
      }

      fetchSessions();
      sessionsApi.get(activeId, token).then(setSession).catch(() => {});

    } catch (err) {
      setError(err.message || 'Failed to get a response.');
      setMessages(prev => prev.filter(m => m.id !== assistantMsgId || m.content));
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden bg-white">

      {/* ── Sidebar ── */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-gray-50 border-r border-gray-100 flex flex-col transition-all duration-300 overflow-hidden shrink-0`}>
        <div className="p-3 flex-shrink-0">
          <button onClick={createNewChat}
            className="w-full flex items-center justify-center gap-2 bg-gray-900 text-white py-2.5 rounded-xl hover:bg-gray-700 transition-all text-sm font-medium">
            <Plus className="h-4 w-4" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-2 pb-4">
          <div className="px-2 mb-2 mt-1">
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-1.5">
              <History className="h-3 w-3" /> Recent Chats
            </h3>
          </div>

          {sessionsLoading ? (
            <div className="py-10 flex justify-center">
              <Loader2 className="h-5 w-5 animate-spin text-gray-300" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="px-4 py-8 text-center">
              <p className="text-xs text-gray-400 italic">No chats yet</p>
            </div>
          ) : (
            <div className="space-y-0.5">
              {sessions.map((s) => (
                <div key={s.id} onClick={() => navigate(`/assistant/${s.id}`)}
                  className={`group flex items-center gap-2.5 px-3 py-2 rounded-lg cursor-pointer transition-all
                    ${sessionId === s.id ? 'bg-amber-50 text-amber-900' : 'text-gray-600 hover:bg-white'}`}>
                  <MessageSquare className={`h-3.5 w-3.5 shrink-0 ${sessionId === s.id ? 'text-amber-500' : 'text-gray-400'}`} />
                  <span className="text-xs truncate flex-1">{s.title}</span>
                  <button onClick={(e) => deleteSession(e, s.id)}
                    className="opacity-0 group-hover:opacity-100 p-0.5 hover:text-red-500 transition-opacity">
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-3 border-t border-gray-100">
          <Link to="/search" className="flex items-center gap-2.5 px-3 py-2 text-xs text-gray-500 hover:text-gray-900 rounded-lg transition-colors">
            <Search className="h-3.5 w-3.5" />
            Search Legal Database
          </Link>
        </div>
      </div>

      {/* ── Main Chat Area ── */}
      <div className="flex-1 flex flex-col min-w-0 relative bg-white">

        {/* Sidebar toggle */}
        <button onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute left-3 top-3 z-10 p-1.5 rounded-lg border border-gray-200/80 bg-white hover:bg-gray-50 transition-all shadow-sm">
          {sidebarOpen ? <X className="h-3.5 w-3.5 text-gray-500" /> : <Menu className="h-3.5 w-3.5 text-gray-500" />}
        </button>

        {/* ── Chat Feed ── */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto w-full px-6 pt-14 pb-4">

            {histLoading ? (
              <div className="flex flex-col items-center justify-center h-full py-20 text-gray-400">
                <Loader2 className="h-6 w-6 animate-spin mb-3" />
                <p className="text-sm">Loading...</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-12 h-12 bg-amber-50 border border-amber-100 rounded-xl flex items-center justify-center mb-5">
                  <Bot className="h-6 w-6 text-amber-500" />
                </div>
                <h2 className="text-lg font-semibold text-gray-900 mb-1">JurisFind Assistant</h2>
                <p className="text-sm text-gray-400 max-w-xs mb-8">
                  Analyze legal documents, search for precedents, or ask general legal questions.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-md">
                  {[
                    'What are the key facts in the Balaji case?',
                    'Summarize the Indian Evidence Act.',
                    'How to draft an eviction notice?',
                    'Explain IP infringement in software.'
                  ].map(t => (
                    <button key={t} onClick={() => setQuestion(t)}
                      className="p-3 text-left text-xs text-gray-600 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl transition-all">
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m, i) => <Message key={m.id || i} msg={m} />)
            )}

            {error && (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl p-3 mb-6 text-red-600 text-xs">
                <AlertCircle className="h-3.5 w-3.5 shrink-0" /> {error}
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        {/* ── Input Area ── */}
        <div className="border-t border-gray-100 px-4 pt-3 pb-4 flex-shrink-0 bg-white">
          <div className="max-w-4xl mx-auto">

            {/* Staged PDF chip — shows above input, inside the form area */}
            {stagedFile && (
              <div className="mb-2 flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 w-fit max-w-full">
                <div className="w-6 h-6 bg-red-500 rounded flex items-center justify-center shrink-0">
                  <FileText className="h-3.5 w-3.5 text-white" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-gray-700 truncate max-w-[200px]">{stagedFile.name}</p>
                  <p className="text-[10px] text-gray-400">PDF</p>
                </div>
                <button onClick={removeStagedFile}
                  className="ml-2 p-0.5 rounded text-gray-400 hover:text-gray-700 transition-colors shrink-0">
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            )}

            <form onSubmit={sendMessage}
              className="relative bg-white border border-gray-200 rounded-2xl shadow-sm focus-within:border-gray-300 focus-within:ring-4 focus-within:ring-gray-900/5 transition-all">

              <textarea
                ref={inputRef}
                rows={1}
                value={question}
                onChange={(e) => {
                  setQuestion(e.target.value);
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 180) + 'px';
                }}
                onKeyDown={handleKeyDown}
                placeholder={sessionId ? "Ask a follow-up or upload a document..." : "Type your legal question here..."}
                disabled={sending}
                className="w-full pl-4 pr-20 py-3.5 resize-none bg-transparent text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none max-h-44 overflow-y-auto disabled:opacity-50"
              />

              <div className="absolute right-2 bottom-2 flex items-center gap-1.5">
                <input type="file" ref={fileRef} className="hidden" onChange={handleFileSelect} accept=".pdf" />
                <button type="button" onClick={() => fileRef.current?.click()}
                  disabled={uploading}
                  title="Attach PDF"
                  className="p-2 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-all disabled:opacity-20">
                  {uploading
                    ? <Loader2 className="h-4 w-4 animate-spin" />
                    : <Paperclip className="h-4 w-4" />}
                </button>
                <button type="submit" disabled={(!question.trim() && !stagedFile) || sending}
                  className="p-2 rounded-lg bg-gray-900 text-white hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-all">
                  {sending
                    ? <Loader2 className="h-4 w-4 animate-spin" />
                    : <Send className="h-4 w-4" />}
                </button>
              </div>
            </form>

            <p className="text-center text-[10px] text-gray-300 mt-2 tracking-wider uppercase">
              JurisFind AI V2 · Groq &amp; Llama-3
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
