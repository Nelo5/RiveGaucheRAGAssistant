export default function Sidebar({ chats, selectedChatId, onSelectChat, onCreateChat }) {
  return (
    <aside className="sidebar">
      <button className="btn new-chat-btn" onClick={onCreateChat}>
        + Новый чат
      </button>
      <ul className="chat-list">
        {chats.map((chat) => (
          <li
            key={chat.id}
            className={`chat-item ${chat.id === selectedChatId ? 'active' : ''}`}
            onClick={() => onSelectChat(chat.id)}
          >
            <div className="chat-title">{chat.title || 'Без названия'}</div>
            <div className="chat-date">{new Date(chat.created_at).toLocaleDateString()}</div>
          </li>
        ))}
      </ul>
    </aside>
  );
}