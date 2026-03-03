import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { getApiUrl, getPdfUrl } from '../config/api';
import { 
  ArrowLeft, 
  FileText, 
  Send, 
  Loader2, 
  AlertCircle,
  CheckCircle,
  Trash2,
  Eye,
  Download,
  Brain,
  User,
  Bot,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const PdfAnalysis = () => {
  const { filename } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const messagesEndRef = useRef(null);
  
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [documentStats, setDocumentStats] = useState(null);
  const [summaryOpen, setSummaryOpen] = useState(false);

  // Get the previous page path, default to '/' if not available
  const previousPage = location.state?.from || '/';

  useEffect(() => {
    if (filename) {
      analyzeDocument();
      getDocumentStats();
    }
  }, [filename]);

  // Removed automatic scrolling behavior

  const analyzeDocument = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use unified endpoint
      const response = await axios.post(getApiUrl('/api/unified/analyze'), {
        filename: filename,
        source: 'database'
      });
      
      if (response.data.success) {
        setAnalysis(response.data);
        // Add initial analysis as first message in chat (preserve any existing user messages)
        setChatHistory(prev => {
          const userMessages = prev.filter(m => !m.isAnalysis);
          return [
            {
              id: 'analysis',
              type: 'bot',
              content: `**Document Analysis Complete**\n\n${response.data.summary || 'Analysis completed successfully.'}`,
              timestamp: new Date(),
              isAnalysis: true
            },
            ...userMessages
          ];
        });
      } else {
        setError('Failed to analyze document');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze document. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getDocumentStats = async () => {
    try {
      const response = await axios.get(getApiUrl(`/api/document-stats/${filename}`));
      if (response.data.success) {
        setDocumentStats(response.data.stats);
      }
    } catch (err) {
      console.error('Stats error:', err);
    }
  };

  const askQuestion = async () => {
    if (!question.trim() || isAsking) return;

    const msgId = Date.now();
    const userMessage = {
      id: `user-${msgId}`,
      type: 'user',
      content: question,
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, userMessage]);
    const currentQuestion = question;
    setQuestion('');
    setIsAsking(true);

    try {
      // Use unified endpoint
      const response = await axios.post(getApiUrl('/api/unified/ask'), {
        question: currentQuestion,
        filename: filename,
        source: 'database'
      });
      
      if (response.data.success) {
        const botMessage = {
          id: `bot-${msgId}`,
          type: 'bot',
          content: response.data.answer,
          timestamp: new Date()
        };
        setChatHistory(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          id: `err-${msgId}`,
          type: 'bot',
          content: "I apologize, but I couldn't process your question. Please try rephrasing it.",
          timestamp: new Date(),
          isError: true
        };
        setChatHistory(prev => [...prev, errorMessage]);
      }
    } catch (err) {
      console.error('Question error:', err);
      const errorMessage = {
        id: `err-${msgId}`,
        type: 'bot',
        content: "I encountered an error while processing your question. Please try again.",
        timestamp: new Date(),
        isError: true
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsAsking(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  const clearChat = () => {
    // Keep only the analysis message, remove all Q&A messages
    const analysisMessage = chatHistory.find(msg => msg.isAnalysis);
    if (analysisMessage) {
      setChatHistory([analysisMessage]);
    } else {
      setChatHistory([]);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const suggestedQuestions = [
    "What are the key legal issues in this case?",
    "Summarize the main arguments presented.",
    "What precedents are cited in this document?",
    "What is the court's final decision?",
    "What are the implications of this ruling?"
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#EAEAE4' }}>
        <div className="text-center">
          <div className="bg-white rounded-2xl border border-gray-200/60 p-8 max-w-sm">
            <div className="bg-gray-900 w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-5">
              <Brain className="h-6 w-6 text-white animate-pulse" />
            </div>
            <h2 className="text-base font-semibold text-gray-900 mb-2">Analyzing Document</h2>
            <p className="text-sm text-gray-500 mb-5">
              Processing &ldquo;<span className="font-medium text-gray-700 break-all">{decodeURIComponent(filename)}</span>&rdquo;
            </p>
            <div className="flex items-center justify-center gap-2 text-gray-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-xs">Please wait...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#EAEAE4' }}>
        <div className="text-center">
          <div className="bg-white rounded-2xl border border-gray-200/60 p-8 max-w-sm">
            <AlertCircle className="h-10 w-10 text-red-400 mx-auto mb-4" />
            <h2 className="text-base font-semibold text-gray-900 mb-2">Analysis Failed</h2>
            <p className="text-sm text-gray-500 mb-5">{error}</p>
            <div className="flex gap-2">
              <button
                onClick={() => navigate(previousPage)}
                className="flex-1 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-full text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Go Back
              </button>
              <button
                onClick={() => analyzeDocument()}
                className="flex-1 px-4 py-2 bg-gray-900 text-white rounded-full text-sm font-medium hover:bg-gray-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EAEAE4' }}>
      {/* Page Header */}
      <div className="bg-white/70 backdrop-blur-sm border-b border-gray-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate(previousPage)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-4 w-4 text-gray-600" />
              </button>
              
              <div className="flex items-center gap-2.5">
                <div className="bg-gray-900 p-2 rounded-lg">
                  <FileText className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h1 className="text-sm font-semibold text-gray-900">Document Analysis</h1>
                  <p className="text-xs text-gray-500 truncate max-w-xs sm:max-w-sm">
                    {decodeURIComponent(filename)}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {documentStats && documentStats.pages && documentStats.words && (
                <div className="hidden sm:flex items-center gap-3 text-xs text-gray-500 mr-2">
                  <span>{documentStats.pages} pages</span>
                  <span>{documentStats.words} words</span>
                </div>
              )}
              
              <a
                href={getPdfUrl(filename)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3.5 py-1.5 bg-white border border-gray-200 text-gray-700 rounded-full text-xs font-medium hover:border-gray-300 transition-colors"
              >
                <Eye className="h-3.5 w-3.5" />
                <span>View</span>
              </a>
              
              <a
                href={getPdfUrl(filename)}
                download={filename}
                className="flex items-center gap-1.5 px-3.5 py-1.5 bg-gray-900 text-white rounded-full text-xs font-medium hover:bg-gray-700 transition-colors"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Download</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
        <div className="flex gap-4" style={{ height: 'calc(100vh - 56px - 88px - 40px)', minHeight: '500px' }}>
          
          {/* Left Side - Q&A Chat Interface */}
          <div className="flex-1 min-w-0">
            <div className="bg-white rounded-2xl border border-gray-200/60 h-full flex flex-col overflow-hidden">
              
              {/* Chat Header */}
              <div className="px-4 sm:px-5 py-3.5 border-b border-gray-100 flex-shrink-0 flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-gray-900">Ask Questions</h2>
                  <p className="text-xs text-gray-400 mt-0.5">Ask about this legal document</p>
                </div>
                <button
                  onClick={clearChat}
                  className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-red-500 px-2.5 py-1.5 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>

              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto px-4 sm:px-5 py-4 space-y-4">
                {chatHistory.filter(msg => !msg.isAnalysis).length === 0 && (
                  <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                    <p className="text-xs font-medium text-gray-400 mb-3 uppercase tracking-wider">Suggested Questions</p>
                    <div className="space-y-1.5">
                      {suggestedQuestions.map((q, index) => (
                        <button
                          key={index}
                          onClick={() => setQuestion(q)}
                          className="w-full text-left px-3 py-2.5 rounded-lg border border-gray-100 hover:border-gray-200 hover:bg-white transition-all text-xs text-gray-600 hover:text-gray-900"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {chatHistory.filter(msg => !msg.isAnalysis).map((message) => (
                  <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`flex items-end gap-2 max-w-[85%] ${message.type === 'user' ? 'flex-row-reverse' : ''}`}>
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.type === 'user' ? 'bg-gray-900' : message.isError ? 'bg-red-400' : 'bg-gray-700'
                      }`}>
                        {message.type === 'user' ? <User className="h-3.5 w-3.5 text-white" /> : <Bot className="h-3.5 w-3.5 text-white" />}
                      </div>
                      <div className={`flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                          message.type === 'user'
                            ? 'bg-gray-900 text-white rounded-br-sm'
                            : message.isError
                              ? 'bg-red-50 border border-red-100 text-red-800 rounded-bl-sm'
                              : 'bg-gray-50 border border-gray-100 text-gray-800 rounded-bl-sm'
                        }`}>
                          {message.type === 'user' ? (
                            <div className="whitespace-pre-wrap">{message.content}</div>
                          ) : (
                            <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-strong:font-semibold prose-headings:font-semibold">
                              <ReactMarkdown>{message.content}</ReactMarkdown>
                            </div>
                          )}
                        </div>
                        <span className="text-xs text-gray-400 mt-1 px-1">{formatTimestamp(message.timestamp)}</span>
                      </div>
                    </div>
                  </div>
                ))}

                {isAsking && (
                  <div className="flex justify-start">
                    <div className="flex items-end gap-2">
                      <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center">
                        <Bot className="h-3.5 w-3.5 text-white" />
                      </div>
                      <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2 text-sm text-gray-500">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Processing...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-gray-100 px-4 sm:px-5 pt-3 pb-4 flex-shrink-0">
                <div className="flex items-end gap-2">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder="Ask about this document..."
                    className="flex-1 px-4 py-3 text-sm border border-gray-200 rounded-xl focus:ring-2 focus:ring-gray-900/10 focus:border-gray-300 resize-none outline-none bg-gray-50 placeholder-gray-400 transition-all"
                    rows="2"
                    disabled={isAsking}
                  />
                  <button
                    onClick={askQuestion}
                    disabled={!question.trim() || isAsking}
                    className="flex-shrink-0 bg-gray-900 hover:bg-gray-700 disabled:bg-gray-200 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  <strong className="text-amber-600">Disclaimer:</strong> AI analysis for informational purposes only.
                </p>
              </div>
            </div>
          </div>

          {/* Right Side - Document Summary (desktop) */}
          <div className="hidden md:flex w-72 lg:w-80 xl:w-96 flex-shrink-0 flex-col bg-white rounded-2xl border border-gray-200/60 overflow-hidden">
            <div className="px-4 py-3.5 border-b border-gray-100 flex-shrink-0">
              <h2 className="text-sm font-semibold text-gray-900">Document Summary</h2>
              <p className="text-xs text-gray-400 mt-0.5">AI-generated legal analysis</p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {analysis && analysis.summary ? (
                <>
                  <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xs font-semibold text-gray-700 flex items-center gap-1.5">
                        <Brain className="h-3.5 w-3.5 text-gray-500" />
                        Legal Analysis
                      </h3>
                      <div className="flex items-center gap-1 text-gray-400">
                        <CheckCircle className="h-3 w-3" />
                        <span className="text-xs">Complete</span>
                      </div>
                    </div>
                    <div className="prose prose-xs max-w-none text-xs text-gray-700 leading-relaxed prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-strong:font-semibold">
                      <ReactMarkdown>{analysis.summary}</ReactMarkdown>
                    </div>
                  </div>

                  {analysis.key_points && (
                    <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                      <h4 className="text-xs font-semibold text-gray-700 mb-2">Key Points</h4>
                      <ul className="space-y-1.5">
                        {Array.isArray(analysis.key_points)
                          ? analysis.key_points.map((point, i) => (
                              <li key={i} className="flex items-start gap-2 text-xs text-gray-600">
                                <div className="w-1 h-1 bg-gray-400 rounded-full mt-1.5 flex-shrink-0" />
                                {point}
                              </li>
                            ))
                          : <li className="text-xs text-gray-600">{analysis.key_points}</li>
                        }
                      </ul>
                    </div>
                  )}

                  <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                    <h4 className="text-xs font-semibold text-gray-700 mb-2">Document Info</h4>
                    <dl className="space-y-1.5 text-xs">
                      <div><dt className="text-gray-400">File</dt><dd className="font-medium text-gray-800 truncate" title={decodeURIComponent(filename)}>{decodeURIComponent(filename)}</dd></div>
                      <div><dt className="text-gray-400">Analysed</dt><dd className="font-medium text-gray-800">{new Date().toLocaleDateString()}</dd></div>
                      {(analysis?.pages || analysis?.page_count || documentStats?.pages) && (
                        <div><dt className="text-gray-400">Pages</dt><dd className="font-medium text-gray-800">{analysis?.pages || analysis?.page_count || documentStats?.pages}</dd></div>
                      )}
                    </dl>
                  </div>
                </>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Brain className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-xs text-gray-400 mb-3">No analysis available</p>
                    <button
                      onClick={analyzeDocument}
                      className="px-4 py-2 bg-gray-900 text-white rounded-full hover:bg-gray-700 transition-colors text-xs font-medium"
                    >
                      Generate Analysis
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Summary Accordion — hidden on md+ where the side panel is visible */}
        {analysis && analysis.summary && (
          <div className="md:hidden mt-4 bg-white rounded-2xl border border-gray-200/60 overflow-hidden">
            <button
              onClick={() => setSummaryOpen(o => !o)}
              className="w-full flex items-center justify-between px-4 py-3.5 text-left"
            >
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-semibold text-gray-900">Document Summary</span>
              </div>
              {summaryOpen ? <ChevronUp className="h-4 w-4 text-gray-400" /> : <ChevronDown className="h-4 w-4 text-gray-400" />}
            </button>

            {summaryOpen && (
              <div className="px-4 pb-4 space-y-3 border-t border-gray-100">
                <div className="bg-gray-50 border border-gray-100 rounded-xl p-4 mt-3">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xs font-semibold text-gray-700 flex items-center gap-1.5">
                      <Brain className="h-3.5 w-3.5 text-gray-500" />
                      Legal Analysis
                    </h3>
                    <div className="flex items-center gap-1 text-gray-400">
                      <CheckCircle className="h-3 w-3" />
                      <span className="text-xs">Complete</span>
                    </div>
                  </div>
                  <div className="prose prose-xs max-w-none text-xs text-gray-700 leading-relaxed prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-strong:font-semibold">
                    <ReactMarkdown>{analysis.summary}</ReactMarkdown>
                  </div>
                </div>

                {analysis.key_points && (
                  <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                    <h4 className="text-xs font-semibold text-gray-700 mb-2">Key Points</h4>
                    <ul className="space-y-1.5">
                      {Array.isArray(analysis.key_points)
                        ? analysis.key_points.map((point, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-gray-600">
                              <div className="w-1 h-1 bg-gray-400 rounded-full mt-1.5 flex-shrink-0" />
                              {point}
                            </li>
                          ))
                        : <li className="text-xs text-gray-600">{analysis.key_points}</li>
                      }
                    </ul>
                  </div>
                )}

                <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                  <h4 className="text-xs font-semibold text-gray-700 mb-2">Document Info</h4>
                  <dl className="space-y-1.5 text-xs">
                    <div><dt className="text-gray-400">File</dt><dd className="font-medium text-gray-800 break-all">{decodeURIComponent(filename)}</dd></div>
                    <div><dt className="text-gray-400">Analysed</dt><dd className="font-medium text-gray-800">{new Date().toLocaleDateString()}</dd></div>
                    {(analysis?.pages || analysis?.page_count || documentStats?.pages) && (
                      <div><dt className="text-gray-400">Pages</dt><dd className="font-medium text-gray-800">{analysis?.pages || analysis?.page_count || documentStats?.pages}</dd></div>
                    )}
                  </dl>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PdfAnalysis;
