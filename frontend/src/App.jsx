import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import SearchPage from './pages/SearchPage';
import PdfAnalysis from './pages/PdfAnalysis';
import LegalChatbot from './pages/LegalChatbot';
import ConfidentialUpload from './pages/ConfidentialUpload';

function App() {
  return (
    <Router>
      <div className="min-h-screen" style={{ backgroundColor: '#EAEAE4' }}>
        <Navigation />
        <main>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/analyze/:filename" element={<PdfAnalysis />} />
            <Route path="/legal-chat" element={<LegalChatbot />} />
            <Route path="/confidential-upload" element={<ConfidentialUpload />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
