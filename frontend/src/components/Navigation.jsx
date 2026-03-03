import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Scale, Menu, X } from 'lucide-react';

function Navigation() {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { path: '/search', label: 'Search' },
    { path: '/legal-chat', label: 'Assistant' },
    { path: '/confidential-upload', label: 'Analysis' },
  ];

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200/60 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="bg-gray-900 p-1.5 rounded-lg">
              <Scale className="h-4 w-4 text-white" />
            </div>
            <span className="text-base font-semibold text-gray-900 tracking-tight">JurisFind</span>
          </Link>

          {/* Desktop Links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3.5 py-1.5 text-sm rounded-lg transition-colors ${
                  location.pathname === link.path
                    ? 'text-gray-900 font-medium bg-gray-100'
                    : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right Side */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              to="/search"
              className="text-sm bg-gray-900 text-white px-4 py-1.5 rounded-full font-medium hover:bg-gray-700 transition-colors"
            >
              Get started
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-3 border-t border-gray-100 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`block px-3 py-2 rounded-lg text-sm transition-colors ${
                  location.pathname === link.path
                    ? 'text-gray-900 font-medium bg-gray-100'
                    : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <div className="pt-2 border-t border-gray-100 flex flex-col gap-1">
              <Link
                to="/search"
                className="block px-3 py-2 text-sm bg-gray-900 text-white rounded-full text-center font-medium"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Get started
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navigation;
