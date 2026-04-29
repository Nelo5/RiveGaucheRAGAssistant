export default function Message({ role, content }) {
  const className = `message ${role}`;
  return (
    <div className={className}>
      <div className="message-role">{role === 'user' ? 'Вы' : role === 'assistant' ? 'Бот' : 'Система'}</div>
      <div className="message-content">{content}</div>
    </div>
  );
}