import { useState, useRef, useEffect } from 'react';
import Message from './Message';

export default function ChatArea({ messages, onSend, placeholder }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput('');
    // автоматически изменяем высоту textarea обратно
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    // авто-расширение textarea
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
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
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="message-input"
          rows="1"
        />
        <button type="submit" className="btn send-btn">Отправить</button>
      </form>
    </div>
  );
}