import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';

import { AuthProvider } from './context/AuthContext';
import ProtectedRoute   from './components/ProtectedRoute';
import Navigation       from './components/Navigation';
import Footer           from './components/Footer';

// Pages
import LandingPage   from './pages/LandingPage';
import SearchPage    from './pages/SearchPage';
import PdfAnalysis   from './pages/PdfAnalysis';
import LegalChatbot  from './pages/LegalChatbot';
import AnalysisPage  from './pages/AnalysisPage';
import LoginPage     from './pages/LoginPage';
import ChatPage      from './pages/ChatPage';

// Inner layout — hides Footer on /login
function AppLayout() {
  const location = useLocation();
  const hideFooter = location.pathname === '/login';

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EAEAE4' }}>
      {/* Hide nav on login page too so it's fully standalone */}
      {!hideFooter && <Navigation />}
      <main>
        <Routes>
          {/* ── Fully public ─────────────────────────────────── */}
          <Route path="/"      element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />}   />

          {/* ── Auth-gated ────────────────────────────────────── */}
          <Route path="/search" element={
            <ProtectedRoute><SearchPage /></ProtectedRoute>
          } />
          <Route path="/analyze/:filename" element={
            <ProtectedRoute><PdfAnalysis /></ProtectedRoute>
          } />
          <Route path="/legal-chat" element={
            <ProtectedRoute><LegalChatbot /></ProtectedRoute>
          } />
          <Route path="/analysis" element={
            <ProtectedRoute><AnalysisPage /></ProtectedRoute>
          } />
          {/* Legacy redirects */}
          <Route path="/confidential-upload" element={<Navigate to="/analysis" replace />} />
          <Route path="/documents"           element={<Navigate to="/analysis" replace />} />
          <Route path="/chat/:sessionId" element={
            <ProtectedRoute><ChatPage /></ProtectedRoute>
          } />
        </Routes>
      </main>
      {!hideFooter && <Footer />}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppLayout />
      </Router>
    </AuthProvider>
  );
}

export default App;
