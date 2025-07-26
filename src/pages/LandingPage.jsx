import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, Brain, Shield, Zap, CheckCircle, MessageSquare, Upload } from 'lucide-react';

function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Advanced natural language processing for intelligent legal research"
    },
    {
      icon: Zap,
      title: "Instant Results",
      description: "Get relevant case law and precedents in seconds, not hours"
    },
    {
      icon: Shield,
      title: "Secure Platform",
      description: "Enterprise-grade security with complete client confidentiality"
    },
    {
      icon: FileText,
      title: "Comprehensive Database",
      description: "Access to extensive legal case database and court decisions"
    }
  ];

  const services = [
    {
      icon: Search,
      title: "Legal Search",
      description: "Search through thousands of legal cases and precedents",
      path: "/search",
      color: "from-blue-600 to-indigo-600"
    },
    {
      icon: MessageSquare,
      title: "Legal Assistant",
      description: "AI-powered legal consultation and Q&A",
      path: "/legal-chat",
      color: "from-green-600 to-emerald-600"
    },
    {
      icon: Upload,
      title: "Private Analysis",
      description: "Upload and analyze confidential legal documents",
      path: "/confidential-upload",
      color: "from-purple-600 to-violet-600"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative container mx-auto px-4 py-20 max-w-6xl">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
              Professional Legal Research
            </h1>
            <p className="text-xl md:text-2xl font-light mb-8 max-w-3xl mx-auto leading-relaxed">
              Advanced AI-powered legal case research platform. Search through comprehensive legal databases, 
              analyze complex cases, and access professional legal insights with enterprise-grade security.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <button
                onClick={() => navigate('/search')}
                className="bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold text-lg
                         hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl 
                         transform hover:scale-105"
              >
                Start Searching
              </button>
              <button
                onClick={() => navigate('/legal-chat')}
                className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-xl 
                         font-semibold text-lg hover:bg-white hover:text-blue-600 
                         transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Try AI Assistant
              </button>
            </div>

            {/* Status Bar */}
            <div className="flex flex-wrap justify-center items-center space-x-6 text-sm font-medium">
              <div className="flex items-center space-x-2 bg-white bg-opacity-20 px-4 py-2 rounded-full">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>AI System Online</span>
              </div>
              <div className="flex items-center space-x-2 bg-white bg-opacity-20 px-4 py-2 rounded-full">
                <CheckCircle className="h-4 w-4 text-green-400" />
                <span>100,000+ Legal Cases</span>
              </div>
              <div className="flex items-center space-x-2 bg-white bg-opacity-20 px-4 py-2 rounded-full">
                <Shield className="h-4 w-4 text-blue-300" />
                <span>Enterprise Security</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Services Section */}
      <div className="py-16 bg-white">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Legal Services
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Choose from our comprehensive suite of AI-powered legal research tools
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <div
                key={index}
                onClick={() => navigate(service.path)}
                className="group p-8 bg-white rounded-2xl shadow-lg hover:shadow-2xl 
                         transition-all duration-300 border border-gray-100 hover:border-blue-200 
                         transform hover:-translate-y-2 cursor-pointer"
              >
                <div className={`bg-gradient-to-r ${service.color} w-16 h-16 rounded-2xl 
                              flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <service.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{service.title}</h3>
                <p className="text-gray-600 leading-relaxed mb-4">{service.description}</p>
                <div className="flex items-center text-blue-600 font-medium group-hover:text-blue-700">
                  <span>Get Started</span>
                  <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" 
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Enterprise Legal Research Platform
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Powered by cutting-edge artificial intelligence and machine learning technologies, 
              designed specifically for legal professionals and law firms requiring the highest standards of accuracy and security.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="group p-6 bg-white rounded-xl 
                                        hover:shadow-lg transition-all duration-300 border border-gray-100
                                        hover:border-blue-200 transform hover:-translate-y-1">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 w-12 h-12 rounded-lg 
                              flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16 bg-white">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Ready to Transform Your Legal Research?
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of legal professionals who trust LegalSearch for their research needs.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/search')}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl 
                       font-semibold text-lg hover:from-blue-700 hover:to-indigo-700 
                       transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              Start Your Search
            </button>
            <button
              onClick={() => navigate('/legal-chat')}
              className="bg-gray-100 text-gray-800 px-8 py-4 rounded-xl font-semibold text-lg 
                       hover:bg-gray-200 transition-all duration-200 shadow-md hover:shadow-lg"
            >
              Ask AI Assistant
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
