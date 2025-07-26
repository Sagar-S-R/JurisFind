import React from 'react';
import { Scale, Shield } from 'lucide-react';

function Footer() {
  return (
    <footer className="bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 text-white mt-16">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="bg-gradient-to-r from-blue-400 to-indigo-400 p-2 rounded-lg">
                <Scale className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">
                LegalSearch
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
              <li><a href="#" className="hover:text-blue-300 transition-colors">Case Research</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">Legal Analysis</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">Document Review</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">Precedent Search</a></li>
            </ul>
          </div>

          {/* Platform */}
          <div>
            <h3 className="font-semibold text-white mb-4">Platform Features</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><a href="#" className="hover:text-blue-300 transition-colors">AI Assistant</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">Enterprise Security</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">API Access</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">System Integration</a></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-semibold text-white mb-4">Support & Legal</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li><a href="#" className="hover:text-blue-300 transition-colors">Help Center</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-blue-300 transition-colors">Contact Support</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © 2025 LegalSearch. All rights reserved. Professional legal research platform.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-blue-300 transition-colors">
              <span className="sr-only">Privacy Policy</span>
              <Shield className="h-4 w-4" />
            </a>
            <a href="#" className="text-gray-400 hover:text-blue-300 transition-colors">
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
