import React from 'react';
import { Link } from 'react-router-dom';
import { Scale, Shield } from 'lucide-react';

function Footer() {
  return (
    <footer className="bg-gradient-to-r from-gray-900 via-purple-900 to-violet-900 text-white mt-16">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="bg-gradient-to-r from-purple-400 to-violet-400 p-2 rounded-lg">
                <Scale className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">
                JurisFind
              </span>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed">
              Professional AI-powered legal research platform designed for legal professionals, delivering precise case analysis and intelligent legal insights with enterprise-grade security and confidentiality.
            </p>
          </div>

          {/* Legal Services */}
          <div>
            <h3 className="font-semibold text-white mb-4">Legal Services</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><Link to="/search" className="hover:text-purple-300 transition-colors">Case Research</Link></li>
              <li><Link to="/legal-chat" className="hover:text-purple-300 transition-colors">Legal Analysis</Link></li>
              <li><Link to="/confidential-upload" className="hover:text-purple-300 transition-colors">Document Review</Link></li>
              <li><Link to="/search" className="hover:text-purple-300 transition-colors">Precedent Search</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-semibold text-white mb-4">Support & Legal</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><a href="#help" className="hover:text-purple-300 transition-colors">Help Center</a></li>
              <li><a href="#terms" className="hover:text-purple-300 transition-colors">Terms of Service</a></li>
              <li><a href="#privacy" className="hover:text-purple-300 transition-colors">Privacy Policy</a></li>
              <li><a href="#contact" className="hover:text-purple-300 transition-colors">Contact Support</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2025 JurisFind. All rights reserved. Professional legal research platform.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#privacy" className="text-gray-400 hover:text-purple-300 transition-colors">
              <span className="sr-only">Privacy Policy</span>
              <Shield className="h-4 w-4" />
            </a>
            <a href="#terms" className="text-gray-400 hover:text-purple-300 transition-colors">
              <span className="sr-only">Terms of Service</span>
              <Scale className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
