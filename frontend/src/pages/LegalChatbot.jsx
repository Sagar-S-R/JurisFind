import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { getApiUrl } from "../config/api";
import {
  Send,
  Trash2,
  Scale,
  Loader2,
  User,
  Bot,
  Menu,
  X,
  ChevronRight,
} from "lucide-react";

const LegalChatbot = () => {
  const messagesContainerRef = useRef(null);

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Scroll the CONTAINER, not the window — avoids page-level scroll caused by footer
  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    if (messages.length > 0 || isLoading) {
      scrollToBottom();
    }
  }, [messages, isLoading]);

  const sendMessage = async (text) => {
    const msg = text || inputMessage;
    if (!msg.trim() || isLoading) return;

    setMessages((prev) => [
      ...prev,
      { type: "user", content: msg, timestamp: new Date() },
    ]);
    setInputMessage("");
    setIsLoading(true);
    setSidebarOpen(false);

    try {
      const response = await axios.post(getApiUrl("/api/legal-chat"), {
        question: msg,
      });
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content: response.data.response,
          timestamp: new Date(),
          isLegal: response.data.is_legal || false,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          type: "bot",
          content: "I am experiencing technical difficulties. Please try again.",
          timestamp: new Date(),
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => setMessages([]);

  const formatTimestamp = (ts) =>
    new Date(ts).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });

  const suggestedQuestions = [
    "What is the difference between civil and criminal law?",
    "Explain the concept of due process",
    "What are the basic constitutional rights?",
    "How does the appeals process work?",
    "What is the statute of limitations?",
    "Explain contract law basics",
    "What is habeas corpus?",
    "How does bail work in criminal cases?",
  ];

  const legalAreas = [
    "Constitutional Law",
    "Criminal Law",
    "Civil Rights",
    "Contract Law",
    "Family Law",
    "Property Law",
    "Employment Law",
    "Corporate Law",
  ];

  return (
    <div
      className="flex overflow-hidden"
      style={{ height: "calc(100vh - 56px)", backgroundColor: "#EAEAE4" }}
    >
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - light theme */}
      <aside
        className={`fixed lg:relative inset-y-0 left-0 z-30 flex flex-col w-64 xl:w-72 flex-shrink-0 bg-white border-r border-gray-200/60 transition-transform duration-300 ease-in-out ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
        style={{ top: 0, height: "100%" }}
      >
        <div className="flex items-center justify-between px-4 py-3.5 border-b border-gray-100 flex-shrink-0">
          <div className="flex items-center gap-2">
            <div className="bg-gray-900 p-1.5 rounded-lg">
              <Scale className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-sm font-semibold text-gray-900">JurisFind</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-4">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider px-2 mb-2">
            Suggested Questions
          </p>
          <div className="space-y-0.5">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => sendMessage(q)}
                className="w-full text-left px-3 py-2.5 rounded-xl text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-all duration-150 flex items-start gap-2 group"
              >
                <ChevronRight className="h-3 w-3 text-gray-300 group-hover:text-gray-500 flex-shrink-0 mt-0.5" />
                <span className="line-clamp-2 leading-relaxed">{q}</span>
              </button>
            ))}
          </div>
          <div className="mt-5">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider px-2 mb-2">
              Legal Areas
            </p>
            <div className="space-y-0.5">
              {legalAreas.map((area) => (
                <button
                  key={area}
                  onClick={() => sendMessage(`Tell me about ${area.toLowerCase()}`)}
                  className="w-full text-left px-3 py-2 rounded-xl text-xs text-gray-500 hover:text-gray-900 hover:bg-gray-50 transition-all duration-150"
                >
                  {area}
                </button>
              ))}
            </div>
          </div>
        </div>

        {messages.length > 0 && (
          <div className="px-4 py-3 border-t border-gray-100 flex-shrink-0">
            <button
              onClick={clearChat}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all duration-150"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span>Clear conversation</span>
            </button>
          </div>
        )}
      </aside>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <div
          className="flex items-center justify-between px-4 sm:px-5 py-3 border-b border-gray-200/60 flex-shrink-0"
          style={{ backgroundColor: "#EAEAE4" }}
        >
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-xl text-gray-600 hover:bg-gray-200/60 transition-colors"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex-1 px-3 lg:px-0">
            <h1 className="text-sm font-semibold text-gray-900">Legal AI Assistant</h1>
            <p className="text-xs text-gray-400">Ask any legal question</p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-red-500 px-3 py-1.5 rounded-lg hover:bg-red-50 border border-gray-200/60 hover:border-red-100 transition-colors"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Clear</span>
            </button>
          )}
        </div>

        {/* Messages */}
        <div ref={messagesContainerRef} className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`flex items-end gap-2.5 max-w-[85%] sm:max-w-[75%] ${message.type === "user" ? "flex-row-reverse" : ""}`}
                  >
                    <div
                      className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center ${message.type === "user" ? "bg-gray-900" : message.isError ? "bg-red-400" : "bg-gray-700"}`}
                    >
                      {message.type === "user" ? (
                        <User className="h-3.5 w-3.5 text-white" />
                      ) : (
                        <Bot className="h-3.5 w-3.5 text-white" />
                      )}
                    </div>
                    <div className={`flex flex-col ${message.type === "user" ? "items-end" : "items-start"}`}>
                      <div
                        className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${message.type === "user" ? "bg-gray-900 text-white rounded-br-sm" : message.isError ? "bg-red-50 border border-red-100 text-red-800 rounded-bl-sm" : "bg-white border border-gray-200/60 text-gray-800 rounded-bl-sm shadow-sm"}`}
                      >
                        {message.type === "user" ? (
                          <div className="whitespace-pre-wrap">{message.content}</div>
                        ) : (
                          <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-strong:font-semibold">
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                          </div>
                        )}
                      </div>
                      <span className="text-xs text-gray-400 mt-1 px-1">
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-end gap-2.5">
                    <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center">
                      <Bot className="h-3.5 w-3.5 text-white" />
                    </div>
                    <div className="bg-white border border-gray-200/60 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Analyzing your question...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
        </div>

        {/* Input */}
        <div
          className="border-t border-gray-200/60 px-4 sm:px-6 pt-3 pb-4 flex-shrink-0"
          style={{ backgroundColor: "#EAEAE4" }}
        >
          <div className="max-w-3xl mx-auto">
            <div className="relative bg-white rounded-2xl border border-gray-200/60 shadow-sm">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask your legal question... (Enter to send)"
                className="w-full px-4 pt-3.5 pb-10 text-sm text-gray-800 placeholder-gray-400 resize-none outline-none bg-transparent rounded-2xl"
                rows="2"
                disabled={isLoading}
              />
              <button
                onClick={() => sendMessage()}
                disabled={!inputMessage.trim() || isLoading}
                className="absolute bottom-3 right-3 bg-gray-900 hover:bg-gray-700 disabled:bg-gray-200 disabled:cursor-not-allowed text-white p-2 rounded-xl transition-colors"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              <strong className="text-amber-600">Disclaimer:</strong>{" "}
              General legal information only. Consult a qualified attorney for specific advice.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalChatbot;