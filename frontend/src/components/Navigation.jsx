import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Scale, MessageSquare, Shield, Search, Menu, X, User, Home } from 'lucide-react';

function Navigation() {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const navItems = [
    { path: '/', label: 'Home', icon: Home, description: 'JurisFind homepage' },
    { path: '/search', label: 'Legal Search', icon: Search, description: 'Search legal cases and precedents' },
    { path: '/legal-chat', label: 'Legal Assistant', icon: MessageSquare, description: 'AI-powered legal consultation' },
    { path: '/confidential-upload', label: 'Private Analysis', icon: Shield, description: 'Confidential case analysis' },
  ];

  return (
    <nav className="bg-white shadow-xl border-b border-gray-200 sticky top-0 z-50 backdrop-blur-lg bg-white/95">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex justify-between items-center py-4">
          {/* Logo and brand */}
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-purple-600 to-violet-600 p-2.5 rounded-xl shadow-lg transform hover:scale-105 transition-transform">
              <Scale className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent">
                JurisFind
              </h1>
              <p className="text-xs text-gray-500 font-medium tracking-wide">Professional Legal Research Platform</p>
            </div>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    group relative px-4 py-2.5 rounded-xl transition-all duration-200 
                    flex items-center space-x-2.5 font-medium
                    ${isActive 
                      ? 'bg-gradient-to-r from-purple-50 to-violet-50 text-purple-700 shadow-sm border border-purple-100' 
                      : 'hover:bg-gray-50 text-gray-600 hover:text-gray-900'
                    }
                  `}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-purple-600' : 'text-gray-500 group-hover:text-gray-700'}`} />
                  <span className="text-sm">{item.label}</span>
                  {isActive && (
                    <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-purple-600 rounded-full"></div>
                  )}
                </Link>
              );
            })}
          </div>

          {/* User Actions */}
          <div className="hidden lg:flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-3 py-2 rounded-lg border border-gray-200 hover:border-purple-300 transition-colors">
              <div className="h-8 w-8 bg-gradient-to-r from-purple-500 to-violet-500 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm font-medium text-gray-700">User</span>
            </div>
          </div>

          {/* Mobile menu button */}
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="lg:hidden py-4 border-t border-gray-100 bg-white">
            <div className="space-y-2">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                const Icon = item.icon;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`
                      flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
                      ${isActive 
                        ? 'bg-purple-50 text-purple-700 border-l-4 border-purple-600' 
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }
                    `}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <Icon className={`h-5 w-5 ${isActive ? 'text-purple-600' : 'text-gray-500'}`} />
                    <div>
                      <span className="font-medium">{item.label}</span>
                      <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
                    </div>
                  </Link>
                );
              })}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center space-x-3 px-4 py-2">
                <div className="h-10 w-10 bg-gradient-to-r from-purple-500 to-violet-500 rounded-full flex items-center justify-center">
                  <User className="h-5 w-5 text-white" />
                </div>
                <div>
                  <span className="font-semibold text-gray-900">User</span>
                  <p className="text-xs text-gray-500">Account</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navigation;
