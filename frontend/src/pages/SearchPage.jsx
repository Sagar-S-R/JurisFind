import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, Clock, Users, Brain, Eye, Download } from 'lucide-react';
import { getApiUrl, getPdfUrl } from '../config/api';

function SearchPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Convert raw filenames like "abc__court__2019_Judgement.pdf" into readable titles
  const filenameToTitle = (filename) => {
    if (!filename) return 'Legal Case Document';
    return filename
      .replace(/\.pdf$/i, '')
      .replace(/__+/g, ' \u2014 ')
      .replace(/[_]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  };

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
    <div className="min-h-screen" style={{ backgroundColor: '#EAEAE4' }}>
      {/* Search Header */}
      <div className="bg-white/70 backdrop-blur-sm border-b border-gray-200/60">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-10">
          <div className="text-center mb-8">
            <h1 className="font-serif-display text-3xl sm:text-4xl text-gray-900 mb-3" style={{ letterSpacing: '-0.01em' }}>
              Legal Case Search
            </h1>
            <p className="text-sm text-gray-500 max-w-xl mx-auto">
              Search through 50,000+ legal cases and precedents instantly.
            </p>
          </div>
          
          {/* Search Form */}
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto">
            <div className="relative bg-white rounded-2xl shadow-sm border border-gray-200/60 p-1.5 sm:p-2">
              <div className="flex items-center gap-1 sm:gap-2">
                <Search className="h-4 w-4 text-gray-400 ml-2 sm:ml-3 flex-shrink-0" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter your legal query or case details..."
                  className="flex-1 min-w-0 px-1 sm:px-2 py-2.5 text-sm text-gray-800 placeholder-gray-400 border-none outline-none bg-transparent"
                />
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="bg-gray-900 hover:bg-gray-700 disabled:bg-gray-300 text-white px-3 sm:px-5 py-2.5 rounded-xl
                           text-sm font-medium transition-colors flex-shrink-0 flex items-center gap-2"
                >
                  {loading ? (
                    <div className="flex items-center gap-1.5">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span className="hidden sm:inline">Searching</span>
                    </div>
                  ) : (
                    <>
                      <Search className="h-4 w-4 sm:hidden" />
                      <span className="hidden sm:inline">Search Cases</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Suggested Queries */}
      {!results.length && !loading && (
        <div className="py-10">
          <div className="max-w-3xl mx-auto px-4 sm:px-6">
            <p className="text-xs text-gray-400 text-center font-medium uppercase tracking-wider mb-4">Popular Topics</p>
            <div className="flex flex-wrap justify-center gap-2">
              {suggestedQueries.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion)}
                  className="bg-white hover:bg-gray-50 text-gray-600 hover:text-gray-900
                           px-4 py-2 rounded-full border border-gray-200 hover:border-gray-300
                           transition-all duration-200 text-sm"
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
        <div className="py-8">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-base font-semibold text-gray-900">
                {results.length} results found
              </h3>
              <div className="flex items-center gap-1.5 text-xs text-gray-400">
                <Clock className="h-3.5 w-3.5" />
                <span>0.34s</span>
              </div>
            </div>
            
            <div className="space-y-3">
              {results.map((result, index) => (
                <div key={index} className="bg-white border border-gray-200/60 rounded-2xl p-5 sm:p-6
                                          hover:border-gray-300 hover:shadow-sm transition-all duration-200">
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-3">
                    <h4 className="text-sm font-semibold text-gray-900 flex-1">
                      {result.title || filenameToTitle(result.filename)}
                    </h4>
                    <span className="self-start bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap">
                      {Math.round((result.similarity_percentage || result.score * 100 || 80))}% match
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mb-4 leading-relaxed line-clamp-3">
                    {result.content || result.text || (
                      result.filename
                        ? `File: ${filenameToTitle(result.filename)}`
                        : 'Case content and legal analysis...'
                    )}
                  </p>
                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      className="flex items-center gap-1.5 bg-gray-900 hover:bg-gray-700 text-white
                        px-4 py-2 rounded-full text-xs font-medium transition-colors"
                      onClick={() => {
                        if (result.filename) {
                          navigate(`/analyze/${encodeURIComponent(result.filename)}`, {
                            state: { from: '/search' }
                          });
                        }
                      }}
                    >
                      <Brain className="h-3.5 w-3.5" />
                      <span>Analyze</span>
                    </button>
                    <button
                      className="flex items-center gap-1.5 bg-white border border-gray-200 hover:border-gray-300
                        text-gray-700 px-4 py-2 rounded-full text-xs font-medium transition-colors"
                      onClick={() => {
                        if (result.filename) {
                          window.open(getPdfUrl(result.filename), '_blank');
                        }
                      }}
                    >
                      <Eye className="h-3.5 w-3.5" />
                      <span>View PDF</span>
                    </button>
                    <a
                      href={result.filename ? getPdfUrl(result.filename) : '#'}
                      download={result.filename}
                      className="flex items-center gap-1.5 bg-white border border-gray-200 hover:border-gray-300
                        text-gray-700 px-4 py-2 rounded-full text-xs font-medium transition-colors"
                      onClick={(e) => { if (!result.filename) e.preventDefault(); }}
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
    </div>
  );
}

export default SearchPage;