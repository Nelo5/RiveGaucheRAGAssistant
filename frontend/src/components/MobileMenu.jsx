// components/MobileMenu.jsx
import { useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function MobileMenu({
  isAuthenticated,
  chats = [],
  selectedChatId,
  onSelectChat,
  onCreateChat,
  onClose,
  user,
  isAdmin,
  onLogout,
}) {
  // Блокируем прокрутку body при открытом меню
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  const handleSelect = (chatId) => {
    if (onSelectChat) onSelectChat(chatId);
    onClose();
  };

  const handleCreate = () => {
    if (onCreateChat) onCreateChat();
    onClose();
  };

  return (
    <>
      <div className="mobile-menu-overlay" onClick={onClose}></div>
      <div className="mobile-menu">
        <div className="mobile-menu-header">
          <button className="close-menu" onClick={onClose}>✕</button>
        </div>
        {isAuthenticated ? (
          <>
            <div className="mobile-user-info">
              {user?.email} ({user?.role})
            </div>
            <button className="btn new-chat-btn" onClick={handleCreate}>
              + Новый чат
            </button>
            <ul className="chat-list">
              {chats.map((chat) => (
                <li
                  key={chat.id}
                  className={`chat-item ${chat.id === selectedChatId ? 'active' : ''}`}
                  onClick={() => handleSelect(chat.id)}
                >
                  <div className="chat-title">{chat.title || 'Без названия'}</div>
                  <div className="chat-date">{new Date(chat.created_at).toLocaleDateString()}</div>
                </li>
              ))}
            </ul>
            {isAdmin && (
              <Link to="/admin/files" className="btn" onClick={onClose}>
                Управление файлами
              </Link>
            )}
            <button onClick={() => { onLogout(); onClose(); }} className="btn btn-danger">
              Выйти
            </button>
          </>
        ) : (
          <div className="mobile-auth-buttons">
            <Link to="/login" className="btn" onClick={onClose}>Войти</Link>
            <Link to="/register" className="btn" onClick={onClose}>Регистрация</Link>
          </div>
        )}
      </div>
    </>
  );
}