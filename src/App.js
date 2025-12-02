import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import CustomerAuthPage from './pages/CustomerAuthPage';
import VoiceConsultationPage from './pages/VoiceConsultationPage';
import { GlobalStyle } from './styles/GlobalStyle';
import { ThemeProvider } from 'styled-components';
import { theme } from './styles/theme';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Router>
        <Routes>
          {/* 고객 인증 페이지 (시작점) */}
          <Route path="/auth" element={<CustomerAuthPage />} />

          {/* 음성 상담 페이지 */}
          <Route path="/consultation" element={<VoiceConsultationPage />} />

          {/* 상담사 대시보드 */}
          <Route path="/dashboard" element={<Dashboard />} />

          {/* 기본 경로 → 인증 페이지로 리다이렉트 */}
          <Route path="/" element={<Navigate to="/auth" replace />} />

          {/* 404 → 인증 페이지로 리다이렉트 */}
          <Route path="*" element={<Navigate to="/auth" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
