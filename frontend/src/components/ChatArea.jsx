import { useState, useRef, useEffect } from 'react';
import Message from './Message';

export default function ChatArea({ messages, onSend, placeholder }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput('');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-area">
      <div className="messages-container">
        {messages.map((msg, idx) => (
          <Message key={msg.id || idx} role={msg.role} content={msg.content} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          className="message-input"
        />
        <button type="submit" className="btn send-btn">Отправить</button>
      </form>
    </div>
  );
}