import React, { useEffect, useRef } from 'react';

function MessageList({ messages, isLoading }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          {message.role === 'assistant' && (
            <div className="avatar">KT</div>
          )}
          <div className="message-bubble">{message.content}</div>
          {message.role === 'user' && (
            <div className="avatar">나</div>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="message assistant">
          <div className="avatar">KT</div>
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;
