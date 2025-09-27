import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Send, 
  MessageCircle, 
  ArrowLeft, 
  Trash2, 
  Scale, 
  AlertCircle,
  Loader2,
  Shield,
  BookOpen,
  Gavel,
  User,
  Bot,
  Clock,
  CheckCircle
} from 'lucide-react';

const LegalChatbot = () => {
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatStats, setChatStats] = useState(null);
  // Initial welcome message
  useEffect(() => {
    setMessages([
      {
        type: 'bot',
        content: "👋 Welcome to your Professional Legal AI Assistant!\n\nI'm specialized in judicial and legal matters. You can:\n• Ask questions about laws and legal procedures\n• Get explanations of legal concepts\n• Learn about court processes and rights\n• Explore different areas of law\n\nSelect a suggested topic from the left panel or type your legal question directly. How can I assist you today?",
        timestamp: new Date(),
        isWelcome: true
      }
    ]);
    
    getChatStats();
  }, []);

  const getChatStats = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/legal-chat/stats');
      setChatStats(response.data);
    } catch (error) {
      console.error('Failed to get chat stats:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/legal-chat', {
        question: inputMessage
      });

      const botMessage = {
        type: 'bot',
        content: response.data.response,
        timestamp: new Date(),
        isLegal: response.data.is_legal || false
      };

      setMessages(prev => [...prev, botMessage]);
      getChatStats();
    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage = {
        type: 'bot',
        content: "❌ I apologize, but I'm currently experiencing technical difficulties. Please try again in a moment.",
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        type: 'bot',
        content: "👋 Chat cleared! How can I assist you with your legal questions today?",
        timestamp: new Date(),
        isWelcome: true
      }
    ]);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const suggestedQuestions = [
    "What is the difference between civil and criminal law?",
    "Explain the concept of due process",
    "What are the basic constitutional rights?",
    "How does the appeals process work?",
    "What is the statute of limitations?",
    "Explain contract law basics"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Professional Header */}
      <div className="bg-white shadow-xl border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Back to Search"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="bg-gradient-to-r from-green-500 to-emerald-500 p-3 rounded-xl shadow-lg">
                  <MessageCircle className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Legal AI Assistant</h1>
                  <p className="text-sm text-gray-600">Professional Legal Consultation</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Removed the query count display */}
              
              <button
                onClick={clearChat}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors shadow-md hover:shadow-lg"
                title="Clear Chat History"
              >
                <Trash2 className="h-4 w-4" />
                <span className="hidden sm:inline">Clear Chat</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex gap-6" style={{ height: 'calc(100vh - 160px)' }}>
          
          {/* Left Side - Fixed Suggested Questions Panel */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 h-full flex flex-col">
              
              {/* Left Panel Header */}
              <div className="p-4 border-b border-gray-200 flex-shrink-0">
                <h2 className="text-lg font-bold text-gray-900 flex items-center">
                  <Gavel className="h-5 w-5 mr-2 text-blue-500" />
                  Legal Topics
                </h2>
                <p className="text-xs text-gray-600 mt-1">
                  Click on any topic to start your inquiry
                </p>
              </div>

              {/* Left Panel Content - Scrollable */}
              <div className="flex-1 overflow-y-auto p-4">
                <div className="space-y-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(question)}
                      className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition-all duration-200 text-xs text-gray-700 hover:text-blue-700 shadow-sm hover:shadow-md group"
                    >
                      <div className="flex items-start space-x-2">
                        <div className="bg-blue-100 group-hover:bg-blue-200 p-1 rounded-full mt-0.5 transition-colors">
                          <Scale className="h-2.5 w-2.5 text-blue-600" />
                        </div>
                        <span className="leading-relaxed text-xs">{question}</span>
                      </div>
                    </button>
                  ))}
                </div>
                
                {/* Additional Legal Categories */}
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
                    <BookOpen className="h-3 w-3 mr-1 text-green-500" />
                    Legal Areas
                  </h3>
                  <div className="space-y-1">
                    {[
                      "Constitutional Law",
                      "Criminal Law Procedures", 
                      "Civil Rights & Liberties",
                      "Contract Law Basics",
                      "Family Law Matters",
                      "Property Law",
                      "Employment Law",
                      "Corporate Law"
                    ].map((area, index) => (
                      <button
                        key={index}
                        onClick={() => setInputMessage(`Tell me about ${area.toLowerCase()}`)}
                        className="w-full text-left px-3 py-2 rounded-md bg-gray-50 hover:bg-green-50 border border-gray-100 hover:border-green-300 transition-all duration-200 text-xs text-gray-600 hover:text-green-700"
                      >
                        {area}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Fixed Chat Interface */}
          <div className="flex-1 min-w-0">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 h-full flex flex-col">
              
              {/* Chat Header - Fixed */}
              <div className="p-4 border-b border-gray-200 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-gray-900 flex items-center">
                      <MessageCircle className="h-5 w-5 mr-2 text-green-500" />
                      Legal AI Assistant
                    </h2>
                    <p className="text-xs text-gray-600 mt-1">
                      Ask me any legal question and get professional guidance
                    </p>
                  </div>
                  
                  {/* Removed the message count and second clear button */}
                </div>
              </div>

              {/* Chat Messages Area - PROPER SCROLLABLE HEIGHT */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ height: 'calc(100vh - 400px)', minHeight: '400px' }}>
                {messages.map((message, index) => (
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
                            : 'bg-gradient-to-r from-green-500 to-emerald-500'
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
                              : message.isWelcome
                                ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 text-gray-800'
                                : 'bg-gray-50 border border-gray-200 text-gray-800'
                        }`}>
                          <div className="whitespace-pre-wrap leading-relaxed text-sm">
                            {message.content}
                          </div>
                          
                          {message.isLegal && message.type === 'bot' && (
                            <div className="mt-2 pt-2 border-t border-green-300">
                              <div className="flex items-center space-x-1 text-green-700">
                                <Scale className="h-3 w-3" />
                                <span className="text-xs font-medium">Legal Query Verified</span>
                              </div>
                            </div>
                          )}
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
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-2">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center shadow-sm">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
                        <div className="flex items-center space-x-2 text-gray-600">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm">Analyzing your legal question...</span>
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
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={handleKeyPress}
                      placeholder="Ask your legal question here... (Press Enter to send)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition-all duration-200 text-sm shadow-sm"
                      rows="3"
                      disabled={isLoading}
                    />
                  </div>
                  
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 disabled:from-gray-400 disabled:to-gray-400 text-white p-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
                    title="Send Message"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>

                {/* Legal Disclaimer */}
                <div className="mt-3 p-2 bg-amber-50 border border-amber-200 rounded-md">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="h-3 w-3 text-amber-600 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-amber-800 leading-relaxed">
                      <strong>Disclaimer:</strong> This AI provides general legal information for educational purposes only. 
                      Consult qualified attorneys for specific legal advice.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalChatbot;
