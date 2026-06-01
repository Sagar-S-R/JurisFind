import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft, Send, FileText, Loader2, AlertCircle,
  User, Bot, ChevronDown, BookOpen, Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { chatApi, docsApi } from '../config/apiClient';

function TypingDots() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      {[0, 1, 2].map((i) => (
        <span key={i} className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }} />
      ))}
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5
        ${isUser ? 'bg-gray-900' : 'bg-amber-100 border border-amber-200'}`}>
        {isUser
          ? <User className="h-3.5 w-3.5 text-white" />
          : <Bot className="h-3.5 w-3.5 text-amber-700" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed
        ${isUser
          ? 'bg-gray-900 text-white rounded-tr-sm'
          : 'bg-white border border-gray-200/80 text-gray-800 rounded-tl-sm shadow-sm'}`}>
        <p className="whitespace-pre-wrap">{msg.message}</p>
        {msg.timestamp && (
          <p className={`text-[10px] mt-1.5 ${isUser ? 'text-gray-400' : 'text-gray-400'}`}>
            {new Date(msg.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { sessionId } = useParams();
  const navigate      = useNavigate();
  const { token }     = useAuth();

  const [session, setSession]     = useState(null);
  const [messages, setMessages]   = useState([]);
  const [question, setQuestion]   = useState('');
  const [sending, setSending]     = useState(false);
  const [histLoading, setHistLoading] = useState(true);
  const [error, setError]         = useState('');
  const [showScrollBtn, setShowScrollBtn] = useState(false);

  const bottomRef   = useRef(null);
  const listRef     = useRef(null);
  const inputRef    = useRef(null);

  // ── Load session info ────────────────────────────────────────────────────
  useEffect(() => {
    docsApi.getStatus(sessionId, token)
      .then(setSession)
      .catch(() => {});
  }, [sessionId, token]);

  // ── Load chat history ────────────────────────────────────────────────────
  const loadHistory = useCallback(async () => {
    setHistLoading(true);
    try {
      const data = await chatApi.history(sessionId, token);
      setMessages(data.messages ?? []);
    } catch (err) {
      if (err.status !== 404) setError('Could not load chat history.');
    } finally {
      setHistLoading(false);
    }
  }, [sessionId, token]);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  // ── Auto-scroll to bottom ────────────────────────────────────────────────
  const scrollToBottom = (smooth = true) => {
    bottomRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
  };

  useEffect(() => {
    if (!histLoading) scrollToBottom(false);
  }, [histLoading]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const onScroll = () => {
    if (!listRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = listRef.current;
    setShowScrollBtn(scrollHeight - scrollTop - clientHeight > 150);
  };

  // ── Send message ─────────────────────────────────────────────────────────
  const sendMessage = async (e) => {
    e?.preventDefault();
    const q = question.trim();
    if (!q || sending) return;

    setQuestion('');
    setError('');

    // Optimistically add user message
    const tempUserMsg = { role: 'user', message: q, timestamp: new Date().toISOString(), _temp: true };
    setMessages((prev) => [...prev, tempUserMsg]);
    setSending(true);

    try {
      const res = await chatApi.ask(sessionId, q, token);
      // Replace temp + add real assistant reply
      // v1 returns { message }, legacy returns { answer }
      const assistantMsg = {
        role: 'assistant',
        message: res.message ?? res.answer,
        timestamp: new Date().toISOString(),
        message_id: res.message_id,
      };
      setMessages((prev) => [
        ...prev.filter((m) => !m._temp),
        { ...tempUserMsg, _temp: false },
        assistantMsg,
      ]);
    } catch (err) {
      setMessages((prev) => prev.filter((m) => !m._temp));
      setError(err.message || 'Failed to get a response. Please try again.');
      setQuestion(q); // restore
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

  const suggestedQuestions = [
    'Summarise the key facts of this case.',
    'Who are the main parties involved?',
    'What was the final ruling or outcome?',
    'What legal precedents are cited?',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)]" style={{ backgroundColor: '#EAEAE4' }}>

      {/* ── Top bar ── */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-200/60 px-4 sm:px-6 py-3 flex items-center gap-3">
        <button onClick={() => navigate('/analysis')}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-900">
          <ArrowLeft className="h-4 w-4" />
        </button>

        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-7 h-7 rounded-lg bg-amber-50 border border-amber-100
            flex items-center justify-center shrink-0">
            <FileText className="h-3.5 w-3.5 text-amber-600" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">
              {session?.document_name ?? 'Loading…'}
            </p>
            <p className="text-xs text-gray-400">RAG · llama-3.3-70b · all-mpnet-base-v2</p>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-gray-400 hidden sm:inline">Ready</span>
        </div>
      </div>

      {/* ── Message list ── */}
      <div ref={listRef} onScroll={onScroll}
        className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-5 relative">

        {histLoading ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <Loader2 className="h-6 w-6 animate-spin mr-2" />
            Loading history…
          </div>
        ) : messages.length === 0 ? (
          /* Empty state with suggested questions */
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-14 h-14 bg-white border border-gray-200 rounded-2xl
              flex items-center justify-center mb-5 shadow-sm">
              <Sparkles className="h-7 w-7 text-amber-500" />
            </div>
            <h2 className="text-lg font-semibold text-gray-800 mb-1">Ask anything about this document</h2>
            <p className="text-sm text-gray-400 mb-8 max-w-sm">
              I've read and indexed the full document. Ask any legal question and I'll answer from the context.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {suggestedQuestions.map((q) => (
                <button key={q} onClick={() => { setQuestion(q); inputRef.current?.focus(); }}
                  className="flex items-center gap-2 text-left text-sm text-gray-600 bg-white/70
                    hover:bg-white border border-gray-200/60 rounded-xl px-4 py-3
                    hover:shadow-sm transition-all">
                  <BookOpen className="h-3.5 w-3.5 text-gray-400 shrink-0" />
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, i) => <Message key={m.message_id ?? i} msg={m} />)
        )}

        {/* Typing indicator */}
        {sending && (
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-amber-100 border border-amber-200
              flex items-center justify-center shrink-0">
              <Bot className="h-3.5 w-3.5 text-amber-700" />
            </div>
            <div className="bg-white border border-gray-200/80 rounded-2xl rounded-tl-sm shadow-sm">
              <TypingDots />
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50
            border border-red-200 rounded-xl px-4 py-3">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Scroll to bottom button */}
      {showScrollBtn && (
        <button onClick={() => scrollToBottom()}
          className="fixed bottom-24 right-6 w-9 h-9 bg-white border border-gray-200 rounded-full
            shadow-md flex items-center justify-center text-gray-500 hover:text-gray-900
            hover:shadow-lg transition-all z-10">
          <ChevronDown className="h-4 w-4" />
        </button>
      )}

      {/* ── Input bar ── */}
      <div className="bg-white/80 backdrop-blur-md border-t border-gray-200/60 px-4 sm:px-6 py-4">
        <form onSubmit={sendMessage}
          className="flex items-end gap-3 bg-white border border-gray-200 rounded-2xl px-4 py-2.5
            focus-within:border-gray-400 focus-within:ring-2 focus-within:ring-gray-900/5 transition-all">
          <textarea
            ref={inputRef}
            rows={1}
            value={question}
            onChange={(e) => {
              setQuestion(e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about this document…"
            disabled={sending}
            className="flex-1 resize-none bg-transparent text-sm text-gray-800 placeholder:text-gray-300
              focus:outline-none leading-relaxed max-h-32 overflow-y-auto disabled:opacity-50"
          />
          <button type="submit" disabled={!question.trim() || sending}
            className="w-8 h-8 flex items-center justify-center rounded-xl bg-gray-900
              text-white hover:bg-gray-700 transition-colors
              disabled:opacity-30 disabled:cursor-not-allowed shrink-0">
            <Send className="h-3.5 w-3.5" />
          </button>
        </form>
        <p className="text-center text-[10px] text-gray-300 mt-2">
          Shift+Enter for new line · Enter to send
        </p>
      </div>
    </div>
  );
}
