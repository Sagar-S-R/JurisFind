import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getApiUrl, getPdfUrl } from '../config/api';
import { 
  Upload, 
  FileText, 
  Shield, 
  ArrowLeft, 
  CheckCircle, 
  Loader2, 
  AlertCircle,
  Search,
  MessageCircle,
  Download,
  Eye,
  Lock,
  Globe,
  Database,
  Brain,
  Trash2,
  X,
  ArrowDown
} from 'lucide-react';

const ConfidentialUpload = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const SESSION_KEY = 'confidential_upload_state';

  // Restore state from sessionStorage on mount (user navigated back)
  const restoreSession = () => {
    try {
      const saved = sessionStorage.getItem(SESSION_KEY);
      if (saved) return JSON.parse(saved);
    } catch { /* ignore */ }
    return null;
  };

  const saved = restoreSession();

  const [uploadedFile, setUploadedFile] = useState(saved?.uploadedFile || null);
  const [uploading, setUploading] = useState(false);
  const [retrieving, setRetrieving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [similarCases, setSimilarCases] = useState(saved?.similarCases || []);
  const [analysis, setAnalysis] = useState(saved?.analysis || null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(saved?.answer || '');
  const [isAsking, setIsAsking] = useState(false);
  const [hasTriedRetrieve, setHasTriedRetrieve] = useState(saved?.hasTriedRetrieve || false);
  const [showToast, setShowToast] = useState(false);

  const clearSession = () => {
    sessionStorage.removeItem(SESSION_KEY);
    setUploadedFile(null);
    setSimilarCases([]);
    setAnalysis(null);
    setAnswer('');
    setQuestion('');
    setHasTriedRetrieve(false);
    setShowToast(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Persist relevant state to sessionStorage whenever it changes
  useEffect(() => {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify({
        uploadedFile,
        similarCases,
        analysis,
        answer,
        hasTriedRetrieve
      }));
    } catch { /* ignore */ }
  }, [uploadedFile, similarCases, analysis, answer, hasTriedRetrieve]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (file.type !== 'application/pdf') {
        alert('Please select a PDF file only.');
        event.target.value = ''; // Clear the input
        return;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size too large. Maximum 10MB allowed.');
        event.target.value = ''; // Clear the input
        return;
      }
      
      uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(getApiUrl('/api/upload-confidential-pdf'), formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        // Clear sessionStorage so old state doesn't bleed into new upload
        sessionStorage.removeItem(SESSION_KEY);
        setUploadedFile({
          name: file.name,
          size: file.size
        });
        // Clear previous results when new file is uploaded
        setSimilarCases([]);
        setAnalysis(null);
        setAnswer('');
        setQuestion('');
        setHasTriedRetrieve(false);
        
        console.log('Upload successful:', response.data.message);
      } else {
        console.error('Upload failed:', response.data);
        alert('Upload failed. Please try again.');
      }
    } catch (err) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.detail || 'Upload failed. Please try again.';
      alert(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const retrieveSimilarCases = async () => {
    if (!uploadedFile) {
      alert('Please upload a file first.');
      return;
    }

    try {
      setRetrieving(true);
      setHasTriedRetrieve(true);
      console.log('Retrieving similar cases for:', uploadedFile.name);
      
      // Use POST request with query parameters as expected by the backend
      const response = await axios.post(getApiUrl(`/api/retrieve-similar-cases?filename=${encodeURIComponent(uploadedFile.name)}&top_k=5`));
      
      console.log('Retrieve response:', response.data);

      if (response.data.success) {
        setSimilarCases(response.data.similar_cases || []);
        console.log('Found similar cases:', response.data.similar_cases?.length || 0);
      } else {
        console.error('Retrieve failed:', response.data);
        alert('Failed to retrieve similar cases. Please try again.');
      }
    } catch (err) {
      console.error('Retrieve error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to retrieve similar cases. Please ensure your file was uploaded correctly and try again.';
      alert(errorMessage);
    } finally {
      setRetrieving(false);
    }
  };

  const analyzeDocument = async () => {
    if (!uploadedFile) {
      alert('Please upload a file first.');
      return;
    }

    try {
      setAnalyzing(true);
      console.log('Analyzing document:', uploadedFile.name);
      
      // Use unified endpoint
      const response = await axios.post(getApiUrl('/api/unified/analyze'), {
        filename: uploadedFile.name,
        source: 'uploaded'
      });
      
      console.log('Analysis response:', response.data);

      if (response.data.success) {
        const analysisText = response.data.summary || response.data.analysis || 'Analysis completed successfully.';
        setAnalysis(analysisText);
        // Show scroll-hint toast
        setShowToast(true);
        setTimeout(() => setShowToast(false), 5000);
        console.log('Analysis completed successfully');
      } else {
        console.error('Analysis failed:', response.data);
        alert('Failed to analyze document. Please try again.');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to analyze document. Please ensure your file was uploaded correctly and try again.';
      alert(errorMessage);
    } finally {
      setAnalyzing(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim() || !uploadedFile) return;

    try {
      setIsAsking(true);
      // Use unified endpoint
      const response = await axios.post(getApiUrl('/api/unified/ask'), {
        filename: uploadedFile.name,
        question: question.trim(),
        source: 'uploaded'
      });

      if (response.data.success) {
        setAnswer(response.data.answer);
      } else {
        console.error('Question failed:', response.data);
        alert('Failed to process question. Please try again.');
      }
    } catch (err) {
      console.error('Question error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to process question. Please try again.';
      alert(errorMessage);
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

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const securityFeatures = [
    {
      icon: Lock,
      title: "End-to-End Encryption",
      description: "Your documents are encrypted during transmission and processing"
    },
    {
      icon: Shield,
      title: "Temporary Processing",
      description: "Files are automatically deleted after analysis completion"
    },
    {
      icon: Database,
      title: "No Permanent Storage",
      description: "Your confidential data is never stored in our databases"
    }
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EAEAE4' }}>

      {/* Scroll-hint Toast */}
      {showToast && (
        <div className="fixed bottom-5 left-4 right-4 sm:left-1/2 sm:right-auto sm:-translate-x-1/2 z-50 flex items-center gap-2.5 bg-gray-900 text-white text-xs sm:text-sm font-medium px-4 py-2.5 rounded-2xl shadow-lg max-w-sm mx-auto sm:mx-0 sm:w-max">
          <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
          <span className="flex-1">Summary ready &mdash; scroll down to view</span>
          <ArrowDown className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
          <button onClick={() => setShowToast(false)} className="ml-1 text-gray-400 hover:text-white transition-colors flex-shrink-0">
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}
      {/* Page Header */}
      <div className="bg-white/70 backdrop-blur-sm border-b border-gray-200/60">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-serif-display text-2xl sm:text-3xl text-gray-900" style={{ letterSpacing: '-0.01em' }}>
                Private Case Analysis
              </h1>
              <p className="text-sm text-gray-500 mt-1">Confidential document processing</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-full">
              <Lock className="h-3.5 w-3.5 text-gray-600" />
              <span className="text-xs font-medium text-gray-600">Secure</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {/* Security Features Banner */}
        <div className="bg-white/70 rounded-2xl border border-gray-200/60 p-5 sm:p-6 mb-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Shield className="h-4 w-4 text-gray-600" />
            Privacy & Security
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {securityFeatures.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div key={index} className="flex items-start gap-3">
                  <div className="bg-gray-100 p-2 rounded-lg flex-shrink-0">
                    <IconComponent className="h-4 w-4 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-gray-900 mb-0.5">{feature.title}</h3>
                    <p className="text-xs text-gray-500 leading-relaxed">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-2xl border border-gray-200/60 mb-5">
          <div className="p-5 sm:p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                <Upload className="h-4 w-4 text-gray-600" />
                Upload Confidential Document
              </h2>
              {/* Delete session button — appears here once file is uploaded */}
              {uploadedFile && (
                <button
                  onClick={clearSession}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 border border-red-200 text-red-600 rounded-full text-xs font-medium transition-colors flex-shrink-0"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">Delete Session</span>
                  <span className="sm:hidden">Delete</span>
                </button>
              )}
            </div>

            {!uploadedFile ? (
              <div className="border-2 border-dashed border-gray-200 rounded-xl p-10 sm:p-12 text-center hover:border-gray-300 transition-colors">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  accept=".pdf"
                  className="hidden"
                />
                
                <div className="space-y-4">
                  <div className="bg-gray-900 w-14 h-14 rounded-2xl flex items-center justify-center mx-auto">
                    <FileText className="h-7 w-7 text-white" />
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-1">
                      Drop your PDF here or click to browse
                    </h3>
                    <p className="text-xs text-gray-500">
                      Maximum 10MB · PDF files only
                    </p>
                  </div>

                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white px-6 py-2.5 rounded-full text-sm font-medium transition-colors inline-flex items-center gap-2"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Uploading...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4" />
                        <span>Select PDF File</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
                <div className="flex items-center gap-3">
                  <div className="bg-gray-900 p-2.5 rounded-lg flex-shrink-0">
                    <CheckCircle className="h-5 w-5 text-white" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold text-gray-900 truncate" title={uploadedFile.name}>{uploadedFile.name}</h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {formatFileSize(uploadedFile.size)} &middot; Uploaded successfully
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setUploadedFile(null);
                      setSimilarCases([]);
                      setAnalysis(null);
                      setAnswer('');
                      setQuestion('');
                      setHasTriedRetrieve(false);
                      if (fileInputRef.current) fileInputRef.current.value = '';
                    }}
                    title="Change file"
                    className="text-gray-400 hover:text-gray-600 p-1.5 hover:bg-gray-200 rounded-lg transition-colors flex-shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Analysis Options */}
        {uploadedFile && (
          <div className="bg-white rounded-2xl border border-gray-200/60 mb-5">
            <div className="p-5 sm:p-6">
              <h2 className="text-base font-semibold text-gray-900 mb-5 flex items-center gap-2">
                <Brain className="h-4 w-4 text-gray-600" />
                Analysis Options
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Retrieve Similar Cases */}
                <div className="bg-gray-50 border border-gray-100 rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <Search className="h-4 w-4 text-gray-600" />
                    <h3 className="text-sm font-semibold text-gray-900">Find Similar Cases</h3>
                  </div>
                  <p className="text-xs text-gray-500 mb-4 leading-relaxed">
                    Search our database for cases similar to your uploaded document.
                  </p>
                  <button
                    onClick={retrieveSimilarCases}
                    disabled={retrieving}
                    className="w-full bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white py-2.5 rounded-full text-sm font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {retrieving ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /><span>Searching...</span></>
                    ) : (
                      <><Search className="h-4 w-4" /><span>Find Similar Cases</span></>
                    )}
                  </button>
                </div>

                {/* Document Analysis */}
                <div className="bg-gray-50 border border-gray-100 rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <MessageCircle className="h-4 w-4 text-gray-600" />
                    <h3 className="text-sm font-semibold text-gray-900">Analyze & Chat</h3>
                  </div>
                  <p className="text-xs text-gray-500 mb-4 leading-relaxed">
                    Get an AI-powered summary and ask specific questions about this document.
                  </p>
                  <button
                    onClick={analyzeDocument}
                    disabled={analyzing}
                    className="w-full bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white py-2.5 rounded-full text-sm font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {analyzing ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /><span>Analyzing...</span></>
                    ) : (
                      <><MessageCircle className="h-4 w-4" /><span>Summarize & Q&A</span></>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Similar Cases Results */}
        {similarCases.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200/60 mb-5">
            <div className="p-5 sm:p-6">
              <h2 className="text-base font-semibold text-gray-900 mb-5 flex items-center gap-2">
                <Database className="h-4 w-4 text-gray-600" />
                Similar Cases Found ({similarCases.length})
              </h2>
              
              <div className="space-y-3">
                {similarCases.map((caseItem, index) => (
                  <div key={index} className="border border-gray-200/60 rounded-xl p-4 sm:p-5 hover:border-gray-300 transition-colors">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <FileText className="h-4 w-4 text-gray-500 flex-shrink-0" />
                        <h3 className="text-sm font-semibold text-gray-900 truncate">
                          {caseItem.title || (caseItem.filename || caseItem.name
                            ? (caseItem.filename || caseItem.name)
                                .replace(/\.pdf$/i, '')
                                .replace(/__+/g, ' \u2014 ')
                                .replace(/[_]+/g, ' ')
                                .trim()
                            : 'Unknown Document')}
                        </h3>
                      </div>
                      <span className="self-start sm:self-auto px-2.5 py-1 bg-gray-100 text-gray-600 text-xs rounded-full font-medium whitespace-nowrap">
                        {((caseItem.score || caseItem.similarity || 0) * 100).toFixed(1)}% match
                      </span>
                    </div>
                    
                    <p className="text-xs text-gray-500 leading-relaxed mb-4 line-clamp-2">
                      {caseItem.content || caseItem.text || 'Legal case document available for analysis.'}
                    </p>
                    
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => navigate(`/analyze/${encodeURIComponent(caseItem.filename || caseItem.name || '')}`, { state: { from: '/confidential-upload' } })}
                        className="flex items-center gap-1.5 px-4 py-2 bg-gray-900 hover:bg-gray-700 text-white rounded-full text-xs font-medium transition-colors"
                      >
                        <Brain className="h-3.5 w-3.5" />
                        <span>Analyze</span>
                      </button>
                      <button
                        onClick={() => window.open(getPdfUrl(caseItem.filename || caseItem.name || ''), '_blank')}
                        className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 hover:border-gray-300 text-gray-700 rounded-full text-xs font-medium transition-colors"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        <span>View</span>
                      </button>
                      <a
                        href={getPdfUrl(caseItem.filename || caseItem.name || '')}
                        download
                        className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 hover:border-gray-300 text-gray-700 rounded-full text-xs font-medium transition-colors"
                      >
                        <Download className="h-3.5 w-3.5" />
                        <span>Download</span>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* No Similar Cases Found Message */}
        {!retrieving && hasTriedRetrieve && similarCases.length === 0 && uploadedFile && (
          <div className="bg-white rounded-2xl border border-gray-200/60 mb-5">
            <div className="p-8 text-center">
              <div className="bg-gray-100 w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3">
                <Search className="h-5 w-5 text-gray-500" />
              </div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">No Similar Cases Found</h3>
              <p className="text-xs text-gray-500 mb-4">
                We couldn't find similar cases for your document.
              </p>
              <button
                onClick={retrieveSimilarCases}
                className="bg-gray-900 hover:bg-gray-700 text-white px-5 py-2 rounded-full text-sm font-medium transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Document Analysis Results */}
        {analysis && (
          <div className="bg-white rounded-2xl border border-gray-200/60 mb-5">
            <div className="p-5 sm:p-6">
              <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Brain className="h-4 w-4 text-gray-600" />
                Document Analysis
              </h2>
              
              <div className="bg-gray-50 border border-gray-100 rounded-xl p-5 mb-5">
                <div className="prose prose-sm max-w-none text-gray-700 prose-p:my-1 prose-ul:my-1 prose-li:my-0 prose-strong:font-semibold">
                  <ReactMarkdown>{analysis}</ReactMarkdown>
                </div>
              </div>

              {/* Q&A Section */}
              <div className="border-t border-gray-100 pt-5">
                <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <MessageCircle className="h-4 w-4 text-gray-600" />
                  Ask Questions
                </h3>
                
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a specific question about this document..."
                    className="flex-1 px-4 py-2.5 text-sm border border-gray-200 rounded-xl bg-gray-50 focus:ring-2 focus:ring-gray-900/10 focus:border-gray-300 outline-none transition-all"
                    disabled={isAsking}
                  />
                  <button
                    onClick={askQuestion}
                    disabled={!question.trim() || isAsking}
                    className="bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap"
                  >
                    {isAsking ? <><Loader2 className="h-4 w-4 animate-spin" /><span>Asking...</span></> : <><MessageCircle className="h-4 w-4" /><span>Ask</span></>}
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
          </div>
        )}
        {/* Clear Session Button removed — now lives in the Upload card header above */}
      </div>
    </div>
  );
};

export default ConfidentialUpload;
