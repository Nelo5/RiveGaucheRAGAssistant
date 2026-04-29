import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function TopBar() {
  const { isAuthenticated, user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="topbar">
      <Link to="/" className="logo">RAG Chat</Link>
      <div className="topbar-actions">
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