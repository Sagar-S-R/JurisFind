import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
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
  Brain
} from 'lucide-react';

const ConfidentialUpload = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [retrieving, setRetrieving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [similarCases, setSimilarCases] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isAsking, setIsAsking] = useState(false);
  const [hasTriedRetrieve, setHasTriedRetrieve] = useState(false);

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

      const response = await axios.post('http://127.0.0.1:8000/api/upload-confidential-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
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
      const response = await axios.post(`http://127.0.0.1:8000/api/retrieve-similar-cases?filename=${encodeURIComponent(uploadedFile.name)}&top_k=5`);
      
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
      
      // Use POST request with query parameter as expected by the backend
      const response = await axios.post(`http://127.0.0.1:8000/api/analyze-confidential-pdf?filename=${encodeURIComponent(uploadedFile.name)}`);
      
      console.log('Analysis response:', response.data);

      if (response.data.success) {
        const analysisText = response.data.summary || response.data.analysis || 'Analysis completed successfully.';
        setAnalysis(analysisText);
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
      const response = await axios.post('http://127.0.0.1:8000/api/ask-question-confidential', {
        filename: uploadedFile.name,
        question: question.trim()
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50">
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
                <div className="bg-gradient-to-r from-purple-500 to-violet-500 p-3 rounded-xl shadow-lg">
                  <Shield className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Private Case Analysis</h1>
                  <p className="text-sm text-gray-600">Confidential Document Processing</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <div className="hidden md:flex items-center space-x-2 px-3 py-2 bg-green-50 border border-green-200 rounded-lg">
                <Lock className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">Secure Environment</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Security Features Banner */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Shield className="h-6 w-6 mr-2 text-purple-500" />
            Your Privacy & Security First
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {securityFeatures.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div key={index} className="flex items-start space-x-3">
                  <div className="bg-purple-100 p-2 rounded-lg">
                    <IconComponent className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 mb-8">
          <div className="p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Upload className="h-6 w-6 mr-2 text-blue-500" />
              Upload Confidential Document
            </h2>

            {!uploadedFile ? (
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-purple-400 transition-colors">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  accept=".pdf"
                  className="hidden"
                />
                
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-purple-500 to-violet-500 w-16 h-16 rounded-full flex items-center justify-center mx-auto">
                    <FileText className="h-8 w-8 text-white" />
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Drop your PDF here or click to browse
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Maximum file size: 10MB. Only PDF files are supported.
                    </p>
                  </div>

                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-600 hover:to-violet-600 disabled:from-gray-400 disabled:to-gray-400 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none flex items-center space-x-2"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        <span>Uploading...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="h-5 w-5" />
                        <span>Select PDF File</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="bg-green-500 p-3 rounded-lg">
                      <CheckCircle className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{uploadedFile.name}</h3>
                      <p className="text-sm text-gray-600">
                        Size: {formatFileSize(uploadedFile.size)} • Uploaded successfully
                      </p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => {
                      setUploadedFile(null);
                      setSimilarCases([]);
                      setAnalysis(null);
                      setAnswer('');
                      setQuestion('');
                      setHasTriedRetrieve(false);
                      fileInputRef.current.value = '';
                    }}
                    className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <AlertCircle className="h-5 w-5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Analysis Options */}
        {uploadedFile && (
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 mb-8">
            <div className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Brain className="h-6 w-6 mr-2 text-indigo-500" />
                Analysis Options
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Retrieve Similar Cases */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <Search className="h-6 w-6 text-blue-500" />
                    <h3 className="text-lg font-semibold text-gray-900">Find Similar Cases</h3>
                  </div>
                  <p className="text-gray-600 mb-4">
                    Search our database for cases similar to your uploaded document based on content analysis.
                  </p>
                  <button
                    onClick={retrieveSimilarCases}
                    disabled={retrieving}
                    className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 disabled:from-gray-400 disabled:to-gray-400 text-white py-3 rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center space-x-2"
                  >
                    {retrieving ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Searching...</span>
                      </>
                    ) : (
                      <>
                        <Search className="h-4 w-4" />
                        <span>Retrieve Similar Cases</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Document Analysis */}
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <MessageCircle className="h-6 w-6 text-green-500" />
                    <h3 className="text-lg font-semibold text-gray-900">Analyze & Chat</h3>
                  </div>
                  <p className="text-gray-600 mb-4">
                    Get an AI-powered summary and ask specific questions about your document.
                  </p>
                  <button
                    onClick={analyzeDocument}
                    disabled={analyzing}
                    className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:from-gray-400 disabled:to-gray-400 text-white py-3 rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center space-x-2"
                  >
                    {analyzing ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <MessageCircle className="h-4 w-4" />
                        <span>Summarize & Q&A</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Similar Cases Results */}
        {similarCases.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 mb-8">
            <div className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Database className="h-6 w-6 mr-2 text-blue-500" />
                Similar Cases Found ({similarCases.length})
              </h2>
              
              <div className="space-y-4">
                {similarCases.map((caseItem, index) => (
                  <div key={index} className="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-200">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <FileText className="h-5 w-5 text-blue-500" />
                          <h3 className="font-semibold text-gray-900">{caseItem.filename || caseItem.name || 'Unknown Document'}</h3>
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                            {((caseItem.score || caseItem.similarity || 0) * 100).toFixed(1)}% match
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <p className="text-gray-700 leading-relaxed text-sm">
                        {(caseItem.content || caseItem.text || 'No preview available').substring(0, 300)}
                        {(caseItem.content || caseItem.text || '').length > 300 ? '...' : ''}
                      </p>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <a
                        href={`http://127.0.0.1:8000/api/pdf/${encodeURIComponent(caseItem.filename || caseItem.name || '')}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                      >
                        <Eye className="h-4 w-4" />
                        <span>View</span>
                      </a>
                      <button
                        onClick={() => navigate(`/analyze/${encodeURIComponent(caseItem.filename || caseItem.name || '')}`, {
                          state: { from: '/confidential-upload' }
                        })}
                        className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                      >
                        <Brain className="h-4 w-4" />
                        <span>Analyze</span>
                      </button>
                      <a
                        href={`http://127.0.0.1:8000/api/pdf/${encodeURIComponent(caseItem.filename || caseItem.name || '')}`}
                        download
                        className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
                      >
                        <Download className="h-4 w-4" />
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
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 mb-8">
            <div className="p-8 text-center">
              <div className="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-gray-500" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Similar Cases Found</h3>
              <p className="text-gray-600 mb-4">
                We couldn't find any similar cases in our database for your uploaded document.
              </p>
              <button
                onClick={retrieveSimilarCases}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Document Analysis Results */}
        {analysis && (
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 mb-8">
            <div className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Brain className="h-6 w-6 mr-2 text-green-500" />
                Document Analysis
              </h2>
              
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 mb-6">
                <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                  {analysis}
                </div>
              </div>

              {/* Q&A Section */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <MessageCircle className="h-5 w-5 mr-2 text-blue-500" />
                  Ask Questions About This Document
                </h3>
                
                <div className="flex space-x-4 mb-4">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a specific question about this document..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    disabled={isAsking}
                  />
                  <button
                    onClick={askQuestion}
                    disabled={!question.trim() || isAsking}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 disabled:from-gray-400 disabled:to-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg flex items-center space-x-2"
                  >
                    {isAsking ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Asking...</span>
                      </>
                    ) : (
                      <>
                        <MessageCircle className="h-4 w-4" />
                        <span>Ask</span>
                      </>
                    )}
                  </button>
                </div>

                {answer && (
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                    <h4 className="font-semibold text-blue-900 mb-2">Answer:</h4>
                    <div className="text-blue-800 whitespace-pre-wrap leading-relaxed">
                      {answer}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfidentialUpload;
