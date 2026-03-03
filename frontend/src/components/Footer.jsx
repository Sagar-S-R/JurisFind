import React from 'react';
import { Link } from 'react-router-dom';
import { Scale } from 'lucide-react';

function Footer() {
  return (
    <footer className="border-t border-gray-200/60" style={{ backgroundColor: '#D8D8D2' }}>
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="flex flex-col md:flex-row justify-between gap-8">
          {/* Brand */}
          <div className="flex items-center gap-2">
            <div className="bg-gray-900 p-1.5 rounded-lg">
              <Scale className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-semibold text-gray-900">JurisFind</span>
          </div>

          {/* Links */}
          <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm text-gray-500">
            <Link to="/search" className="hover:text-gray-900 transition-colors">Case Search</Link>
            <Link to="/legal-chat" className="hover:text-gray-900 transition-colors">AI Assistant</Link>
            <Link to="/confidential-upload" className="hover:text-gray-900 transition-colors">Analysis</Link>
            <a href="#privacy" className="hover:text-gray-900 transition-colors">Privacy</a>
            <a href="#terms" className="hover:text-gray-900 transition-colors">Terms</a>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200/60">
          <p className="text-xs text-gray-400">© 2026 JurisFind. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
