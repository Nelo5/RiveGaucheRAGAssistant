// App.js
import { Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import ChatPage from './pages/ChatPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import FilesPage from './pages/FilesPage';
import NotFound from './pages/NotFound';
import { useAuth } from './contexts/AuthContext';
import TopBar from './components/TopBar';

function ProtectedAdminRoute({ children }) {
  const { user } = useAuth();
  if (!user || user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }
  return children;
}

export default function App() {
  const [isMobileMenuOpen, setMobileMenuOpen] = useState(false);
  const toggleMobileMenu = () => setMobileMenuOpen(prev => !prev);
  const closeMobileMenu = () => setMobileMenuOpen(false);

  return (
    <div className="app">
      <TopBar isMobileMenuOpen={isMobileMenuOpen} onToggleMobileMenu={toggleMobileMenu} />
      <div className="main-content">
        <Routes>
          <Route
            path="/"
            element={<ChatPage isMobileMenuOpen={isMobileMenuOpen} onCloseMobileMenu={closeMobileMenu} />}
          />
          <Route
            path="/chat/:chatId"
            element={<ChatPage isMobileMenuOpen={isMobileMenuOpen} onCloseMobileMenu={closeMobileMenu} />}
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/admin/files"
            element={
              <ProtectedAdminRoute>
                <FilesPage />
              </ProtectedAdminRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </div>
  );
}