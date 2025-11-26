import React, { useState } from 'react';
import PhoneAuth from './components/PhoneAuth';
import ChatRoom from './components/ChatRoom';
import History from './components/History';

function App() {
  const [view, setView] = useState('auth'); // 'auth', 'chat', 'history'
  const [sessionData, setSessionData] = useState(null);
  const [phoneNumber, setPhoneNumber] = useState('');

  const handleAuth = (data) => {
    setSessionData(data);
    setPhoneNumber(data.customer?.phone_number || '');
    setView('chat');
  };

  const handleEndChat = (result) => {
    if (result) {
      console.log('상담 요약:', result.summary);
    }
    setSessionData(null);
    setView('auth');
  };

  const handleShowHistory = () => {
    setView('history');
  };

  const handleBackFromHistory = () => {
    setView('auth');
  };

  return (
    <div className="app">
      {view === 'auth' && (
        <>
          <div className="header">
            <h1>KT AI 상담원</h1>
            <div className="subtitle">요금제 상담 서비스</div>
          </div>
          <PhoneAuth onAuth={handleAuth} onShowHistory={handleShowHistory} />
        </>
      )}

      {view === 'chat' && sessionData && (
        <ChatRoom
          sessionId={sessionData.session_id}
          initialMessage={sessionData.greeting_message}
          customer={sessionData.customer}
          onEnd={handleEndChat}
        />
      )}

      {view === 'history' && (
        <History phoneNumber={phoneNumber} onBack={handleBackFromHistory} />
      )}
    </div>
  );
}

export default App;
