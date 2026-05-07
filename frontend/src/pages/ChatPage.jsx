// pages/ChatPage.jsx
import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';
import Sidebar from '../components/Sidebar';
import ChatArea from '../components/ChatArea';
import MobileMenu from '../components/MobileMenu';

export default function ChatPage({ isMobileMenuOpen, onCloseMobileMenu }) {
  const { chatId } = useParams();
  const { isAuthenticated, token, user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  // Гостевые сообщения
  const [guestMessages, setGuestMessages] = useState([]);

  useEffect(() => {
    if (!isAuthenticated) {
      localStorage.removeItem('guest_messages');
    }
  }, [isAuthenticated]); 

  useEffect(() => {
    if (!isAuthenticated) {
      localStorage.setItem('guest_messages', JSON.stringify(guestMessages));
    }
  }, [guestMessages, isAuthenticated]);

  const sendGuestMessage = async (content) => {
    const question = content.trim();
    if (!question) return;
    const newMessages = [...guestMessages, { role: 'user', content: question }];
    setGuestMessages(newMessages);
    try {
      const response = await api.query(question);
      setGuestMessages((prev) => [...prev, { role: 'assistant', content: response.answer }]);
    } catch (err) {
      setGuestMessages((prev) => [...prev, { role: 'system', content: `Ошибка: ${err.message}` }]);
    }
  };

  // Авторизованный режим
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(chatId || null);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (!isAuthenticated || !token) return;

    const loadChats = async () => {
      try {
        const data = await api.getChats();
        setChats(data);
        if (data.length > 0) {
          if (!selectedChatId) {
            setSelectedChatId(data[0].id);
            navigate(`/chat/${data[0].id}`, { replace: true });
          }
        } else {
          const newChat = await api.createChat();
          setChats([newChat]);
          setSelectedChatId(newChat.id);
          navigate(`/chat/${newChat.id}`, { replace: true });
        }
      } catch (err) {
        console.error('Ошибка загрузки чатов:', err);
      }
    };
    loadChats();
  }, [isAuthenticated, token, navigate, selectedChatId]);

  useEffect(() => {
    if (chatId && isAuthenticated) {
      setSelectedChatId(chatId);
    }
  }, [chatId, isAuthenticated]);

  const loadMessages = useCallback(async () => {
    if (!selectedChatId || !isAuthenticated) return;
    try {
      const data = await api.getMessages(selectedChatId);
      setMessages(data);
    } catch (err) {
      console.error('Ошибка загрузки сообщений:', err);
    }
  }, [selectedChatId, isAuthenticated]);

  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  const sendChatMessage = async (content) => {
    if (!selectedChatId || !content.trim()) return;
    const question = content.trim();
    setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'user', content: question }]);
    try {
      const response = await api.sendMessage(selectedChatId, question);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'system', content: `Ошибка: ${err.message}` }]);
    }
  };

  const handleCreateChat = async () => {
    try {
      const newChat = await api.createChat();
      setChats((prev) => [...prev, newChat]);
      setSelectedChatId(newChat.id);
      setMessages([]);
      navigate(`/chat/${newChat.id}`);
      onCloseMobileMenu();
    } catch (err) {
      console.error('Ошибка создания чата:', err);
    }
  };

  const handleSelectChat = (chatId) => {
    setSelectedChatId(chatId);
    navigate(`/chat/${chatId}`);
    onCloseMobileMenu();
  };

  // Гость
  if (!isAuthenticated) {
    return (
      <div className="chat-layout guest">
        <ChatArea
          messages={guestMessages}
          onSend={sendGuestMessage}
          placeholder="Введите ваш вопрос..."
        />
        {isMobileMenuOpen && (
          <MobileMenu
            isAuthenticated={false}
            onClose={onCloseMobileMenu}
          />
        )}
      </div>
    );
  }

  // Авторизованный
  return (
    <div className="chat-layout authenticated">
      <div className="sidebar-container">
        <Sidebar
          chats={chats}
          selectedChatId={selectedChatId}
          onSelectChat={handleSelectChat}
          onCreateChat={handleCreateChat}
        />
      </div>
      <ChatArea
        messages={messages}
        onSend={sendChatMessage}
        placeholder="Введите сообщение..."
      />
      {isMobileMenuOpen && (
        <MobileMenu
          isAuthenticated={true}
          chats={chats}
          selectedChatId={selectedChatId}
          onSelectChat={handleSelectChat}
          onCreateChat={handleCreateChat}
          onClose={onCloseMobileMenu}
          user={user}
          isAdmin={isAdmin}
          onLogout={logout}
        />
      )}
    </div>
  );
}