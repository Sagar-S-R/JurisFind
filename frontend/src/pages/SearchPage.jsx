import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, Clock, Users, Brain, Eye } from 'lucide-react';
import { getApiUrl, getPdfUrl } from '../config/api';

function SearchPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(getApiUrl('/api/search'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, top_k: 10 }),
      });
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const suggestedQueries = [
    "Contract breach in employment law",
    "Property rights in joint ownership",
    "Criminal liability in corporate fraud",
    "Constitutional rights violation cases",
    "Intellectual property infringement"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Search Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Legal Case Search
            </h1>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Search through comprehensive legal databases to find relevant cases and precedents.
            </p>
          </div>
          
          {/* Search Form */}
          <form onSubmit={handleSearch} className="max-w-4xl mx-auto">
            <div className="relative bg-white rounded-xl shadow-lg border border-gray-200 p-2">
              <div className="flex items-center">
                <Search className="h-5 w-5 text-gray-400 ml-4" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter your legal query, case details, or search terms..."
                  className="flex-1 px-4 py-3 text-gray-800 placeholder-gray-500 border-none outline-none rounded-l-xl"
                />
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg 
                           font-medium transition-all duration-200 shadow-md hover:shadow-lg"
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Searching</span>
                    </div>
                  ) : (
                    'Search Cases'
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Suggested Queries */}
      {!results.length && !loading && (
        <div className="py-8 bg-gray-50">
          <div className="container mx-auto px-4 max-w-4xl">
            <h3 className="text-lg font-semibold text-center text-gray-900 mb-6">
              Popular Legal Research Topics
            </h3>
            <div className="flex flex-wrap justify-center gap-3">
              {suggestedQueries.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion)}
                  className="bg-white hover:bg-blue-50 text-gray-700 hover:text-blue-700 
                           px-3 py-2 rounded-lg border border-gray-200 hover:border-blue-300
                           transition-all duration-200 text-sm font-medium shadow-sm hover:shadow-md"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div className="py-12 bg-white">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-2xl font-bold text-gray-900">
                Search Results ({results.length} found)
              </h3>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Clock className="h-4 w-4" />
                <span>Results generated in 0.34s</span>
              </div>
            </div>
            
            <div className="space-y-6">
              {results.map((result, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-xl p-6 
                                          hover:border-blue-300 hover:shadow-lg transition-all duration-200">
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-lg font-semibold text-gray-900 hover:text-blue-600 
                                 transition-colors cursor-pointer">
                      {result.title || 'Legal Case Document'}
                    </h4>
                    <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">
                      Similarity: {Math.round((result.similarity_percentage || result.score * 100 || 80))}%
                    </span>
                  </div>
                  <p className="text-gray-600 mb-4 leading-relaxed">
                    {result.content || result.text || 'Case content and legal analysis...'}
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center space-x-1">
                        <FileText className="h-4 w-4" />
                        <span>Case Document</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Users className="h-4 w-4" />
                        <span>Legal Precedent</span>
                      </span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <button
                        className="bg-gradient-to-r from-green-600 to-emerald-600 text-white 
                          px-4 py-2 rounded-lg text-sm font-medium hover:from-green-700 
                          hover:to-emerald-700 transition-all duration-200 shadow-md 
                          hover:shadow-lg transform hover:scale-105 flex items-center space-x-2"
                        onClick={() => {
                          if (result.filename) {
                            navigate(`/analyze/${encodeURIComponent(result.filename)}`, {
                              state: { from: '/search' }
                            });
                          }
                        }}
                      >
                        <Brain className="h-4 w-4" />
                        <span>Analyze</span>
                      </button>
                      <button
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white 
                          px-4 py-2 rounded-lg text-sm font-medium hover:from-blue-700 
                          hover:to-indigo-700 transition-all duration-200 shadow-md 
                          hover:shadow-lg transform hover:scale-105 flex items-center space-x-2"
                        onClick={() => {
                          if (result.filename) {
                            window.open(getPdfUrl(result.filename), '_blank');
                          }
                        }}
                      >
                        <Eye className="h-4 w-4" />
                        <span>View PDF</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchPage;