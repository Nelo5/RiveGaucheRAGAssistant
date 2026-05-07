// components/TopBar.jsx
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function TopBar({ isMobileMenuOpen, onToggleMobileMenu }) {
  const { isAuthenticated, user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="hamburger" onClick={onToggleMobileMenu} aria-label="Меню">
          ☰
        </button>
        <Link to="/" className="logo">Рив Гош поддержка</Link>
      </div>
      <div className="topbar-actions desktop-only">
        {isAuthenticated ? (
          <>
            <span className="user-info">{user.email} ({user.role})</span>
            {isAdmin && (
              <Link to="/admin/files" className="btn">Управление файлами</Link>
            )}
            <button onClick={handleLogout} className="btn">Выйти</button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn">Войти</Link>
            <Link to="/register" className="btn">Регистрация</Link>
          </>
        )}
      </div>
    </header>
  );
}