import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { getApiUrl, getPdfUrl } from '../config/api';
import { 
  ArrowLeft, 
  FileText, 
  MessageCircle, 
  Send, 
  Loader2, 
  AlertCircle,
  CheckCircle,
  BarChart3,
  Trash2,
  Eye,
  Download,
  Brain,
  Clock,
  User,
  Bot,
  Scale,
  BookOpen
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
      
      const response = await axios.post(getApiUrl(`/api/analyze-document?filename=${filename}`));
      
      if (response.data.success) {
        setAnalysis(response.data);
        // Add initial analysis as first message in chat
        setChatHistory([
          {
            type: 'bot',
            content: `**Document Analysis Complete**\n\n**Summary:**\n${response.data.summary || 'Analysis completed successfully.'}`,
            timestamp: new Date(),
            isAnalysis: true
          }
        ]);
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

    const userMessage = {
      type: 'user',
      content: question,
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, userMessage]);
    const currentQuestion = question;
    setQuestion('');
    setIsAsking(true);

    try {
      const response = await axios.post(getApiUrl('/api/ask-question'), {
        question: newQuestion,
        filename: filename
      });      if (response.data.success) {
        const botMessage = {
          type: 'bot',
          content: response.data.answer,
          timestamp: new Date()
        };
        setChatHistory(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md">
            <div className="bg-gradient-to-r from-blue-500 to-indigo-500 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
              <Brain className="h-8 w-8 text-white animate-pulse" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Analyzing Document</h2>
            <p className="text-gray-600 mb-6">
              AI is processing "<span className="font-medium">{decodeURIComponent(filename)}</span>" 
              to provide comprehensive legal analysis...
            </p>
            <div className="flex items-center justify-center space-x-2">
              <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
              <span className="text-sm text-gray-500">Please wait...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-red-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-6" />
            <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Failed</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="flex space-x-4">
              <button
                onClick={() => navigate(previousPage)}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Go Back
              </button>
              <button
                onClick={() => analyzeDocument()}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Retry Analysis
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Professional Header */}
      <div className="bg-white shadow-xl border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(previousPage)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Go Back"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="bg-gradient-to-r from-green-500 to-emerald-500 p-3 rounded-xl shadow-lg">
                  <FileText className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Document Analysis</h1>
                  <p className="text-sm text-gray-600 truncate max-w-md">
                    {decodeURIComponent(filename)}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {documentStats && documentStats.pages && documentStats.words && (
                <div className="hidden md:flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <BookOpen className="h-4 w-4 text-blue-500" />
                    <span>{documentStats.pages} pages</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <BarChart3 className="h-4 w-4 text-green-500" />
                    <span>{documentStats.words} words</span>
                  </div>
                </div>
              )}
              
              <div className="flex items-center space-x-2">
                <a
                  href={getPdfUrl(filename)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors shadow-md"
                >
                  <Eye className="h-4 w-4" />
                  <span className="hidden sm:inline">View PDF</span>
                </a>
                
                <button
                  onClick={clearChat}
                  className="flex items-center space-x-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors shadow-md"
                  title="Reset Chat"
                >
                  <Trash2 className="h-4 w-4" />
                  <span className="hidden sm:inline">Reset</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex gap-6" style={{ height: 'calc(100vh - 160px)' }}>
          
          {/* Left Side - Q&A Chat Interface */}
          <div className="flex-1 min-w-0">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 h-full flex flex-col">
              
              {/* Chat Header - Fixed */}
              <div className="p-4 border-b border-gray-200 flex-shrink-0">
                <h2 className="text-lg font-bold text-gray-900 flex items-center">
                  <MessageCircle className="h-5 w-5 mr-2 text-blue-500" />
                  Ask Questions
                </h2>
                <p className="text-xs text-gray-600 mt-1">
                  Ask specific questions about this legal document
                </p>
              </div>

              {/* Chat Messages Area - PROPERLY SCROLLABLE */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ height: 'calc(100vh - 350px)', minHeight: '300px' }}>
                {/* Welcome message with suggested questions */}
                {chatHistory.filter(msg => !msg.isAnalysis).length === 0 && (
                  <div className="mb-6">
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
                      <h3 className="text-md font-semibold text-gray-900 mb-3 flex items-center">
                        <Scale className="h-4 w-4 mr-2 text-blue-500" />
                        Suggested Questions:
                      </h3>
                      <div className="space-y-2">
                        {suggestedQuestions.map((question, index) => (
                          <button
                            key={index}
                            onClick={() => setQuestion(question)}
                            className="w-full text-left p-3 rounded-lg border border-blue-200 hover:border-blue-400 hover:bg-blue-50 transition-all duration-200 text-xs text-gray-700 hover:text-blue-700"
                          >
                            {question}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Chat messages excluding analysis */}
                {chatHistory.filter(msg => !msg.isAnalysis).map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-start space-x-2 max-w-[80%] ${
                      message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                    }`}>
                      {/* Avatar */}
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm ${
                        message.type === 'user' 
                          ? 'bg-gradient-to-r from-blue-500 to-indigo-500' 
                          : message.isError
                            ? 'bg-red-500'
                            : 'bg-gradient-to-r from-purple-500 to-violet-500'
                      }`}>
                        {message.type === 'user' ? (
                          <User className="h-4 w-4 text-white" />
                        ) : (
                          <Bot className="h-4 w-4 text-white" />
                        )}
                      </div>

                      {/* Message Content */}
                      <div className={`flex flex-col ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`rounded-xl px-4 py-3 shadow-sm ${
                          message.type === 'user'
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white'
                            : message.isError
                              ? 'bg-red-50 border border-red-200 text-red-800'
                              : 'bg-gray-50 border border-gray-200 text-gray-800'
                        }`}>
                          <div className="whitespace-pre-wrap leading-relaxed text-sm">
                            {message.content}
                          </div>
                        </div>

                        {/* Timestamp */}
                        <div className={`text-xs text-gray-500 mt-1 flex items-center space-x-1 ${
                          message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                        }`}>
                          <Clock className="h-2.5 w-2.5" />
                          <span>{formatTimestamp(message.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Loading indicator */}
                {isAsking && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-2">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-violet-500 flex items-center justify-center shadow-sm">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
                        <div className="flex items-center space-x-2 text-gray-600">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm">Processing your question...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area - Fixed at Bottom */}
              <div className="border-t border-gray-200 p-4 flex-shrink-0">
                <div className="flex items-end space-x-3">
                  <div className="flex-1">
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      onKeyDown={handleKeyPress}
                      placeholder="Ask about this document..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition-all duration-200 text-sm"
                      rows="2"
                      disabled={isAsking}
                    />
                  </div>
                  
                  <button
                    onClick={askQuestion}
                    disabled={!question.trim() || isAsking}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 disabled:from-gray-400 disabled:to-gray-400 text-white p-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
                    title="Send Question"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>

                {/* Legal Disclaimer */}
                <div className="mt-3 p-2 bg-amber-50 border border-amber-200 rounded-md">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="h-3 w-3 text-amber-600 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-amber-800">
                      <strong>Disclaimer:</strong> AI analysis for informational purposes only. Consult legal professionals for advice.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Document Summary */}
          <div className="w-96 flex-shrink-0">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 h-full flex flex-col">
              
              {/* Summary Header - Fixed */}
              <div className="p-4 border-b border-gray-200 flex-shrink-0">
                <h2 className="text-lg font-bold text-gray-900 flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-green-500" />
                  Document Summary
                </h2>
                <p className="text-xs text-gray-600 mt-1">
                  AI-generated analysis of the legal document
                </p>
              </div>

              {/* Summary Content - PROPERLY SCROLLABLE */}
              <div className="flex-1 overflow-y-auto p-4" style={{ height: 'calc(100vh - 250px)', minHeight: '400px' }}>
                {analysis && analysis.summary ? (
                  <div className="space-y-4">
                    {/* Summary Content */}
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-md font-semibold text-gray-900 flex items-center">
                          <Brain className="h-4 w-4 mr-2 text-green-500" />
                          Legal Analysis
                        </h3>
                        <div className="flex items-center space-x-1 text-green-700">
                          <CheckCircle className="h-3 w-3" />
                          <span className="text-xs font-medium">Complete</span>
                        </div>
                      </div>
                      
                      <div className="text-gray-800">
                        <div className="whitespace-pre-wrap leading-relaxed text-sm">
                          {analysis.summary}
                        </div>
                      </div>
                    </div>

                    {/* Additional Analysis Details */}
                    {analysis.key_points && (
                      <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                          <BarChart3 className="h-3 w-3 mr-2 text-blue-500" />
                          Key Points
                        </h4>
                        <ul className="space-y-1 text-xs text-gray-700">
                          {Array.isArray(analysis.key_points) ? 
                            analysis.key_points.map((point, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                <span>{point}</span>
                              </li>
                            )) :
                            <li className="text-gray-600">{analysis.key_points}</li>
                          }
                        </ul>
                      </div>
                    )}

                    {/* Document Stats */}
                    <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                        <BookOpen className="h-3 w-3 mr-2 text-gray-500" />
                        Document Information
                      </h4>
                      <div className="space-y-2 text-xs">
                        <div>
                          <span className="text-gray-600">Filename:</span>
                          <p className="font-medium text-gray-900 truncate" title={decodeURIComponent(filename)}>
                            {decodeURIComponent(filename)}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-600">Analysis Date:</span>
                          <p className="font-medium text-gray-900">
                            {new Date().toLocaleDateString()}
                          </p>
                        </div>
                        {documentStats && (
                          <>
                            <div>
                              <span className="text-gray-600">Pages:</span>
                              <p className="font-medium text-gray-900">{documentStats.pages || 'N/A'}</p>
                            </div>
                            <div>
                              <span className="text-gray-600">Words:</span>
                              <p className="font-medium text-gray-900">{documentStats.words || 'N/A'}</p>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <Brain className="h-10 w-10 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600 text-sm mb-3">No analysis available</p>
                      <button
                        onClick={analyzeDocument}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                      >
                        Generate Analysis
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PdfAnalysis;
