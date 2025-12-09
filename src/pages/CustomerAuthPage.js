import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import PhoneInput from '../components/auth/PhoneInput';
import BirthDateInput from '../components/auth/BirthDateInput';
import api from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const AuthCard = styled(motion.div)`
  background: white;
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const Logo = styled.div`
  text-align: center;
  margin-bottom: 32px;
`;

const LogoText = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  margin: 0;
`;

const LogoSubtext = styled.p`
  color: #666;
  margin-top: 8px;
  font-size: 14px;
`;

const Title = styled.h2`
  font-size: 24px;
  font-weight: 600;
  color: #333;
  text-align: center;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: #666;
  text-align: center;
  margin-bottom: 32px;
  font-size: 14px;
  line-height: 1.6;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const SubmitButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 16px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  background: #fff5f5;
  border: 1px solid #feb2b2;
  color: #c53030;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
`;

const InfoBox = styled.div`
  background: #f0f4ff;
  border-radius: 12px;
  padding: 16px;
  margin-top: 24px;
`;

const InfoTitle = styled.h4`
  font-size: 14px;
  color: #667eea;
  margin: 0 0 8px 0;
`;

const InfoText = styled.p`
  font-size: 13px;
  color: #666;
  margin: 0;
  line-height: 1.6;
`;

const CustomerAuthPage = () => {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isValid = phone.length >= 10 && birthDate.length === 8;

  // 오디오 자동재생 잠금해제 (브라우저 정책 우회)
  const unlockAudio = () => {
    // AudioContext 생성 및 resume
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
      const ctx = new AudioContext();
      ctx.resume();
      // 무음 재생
      const buffer = ctx.createBuffer(1, 1, 22050);
      const source = ctx.createBufferSource();
      source.buffer = buffer;
      source.connect(ctx.destination);
      source.start();
    }

    // Audio 객체로도 잠금해제
    const audio = new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=');
    audio.play().catch(() => {});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isValid) return;

    // 오디오 잠금해제 (사용자 클릭 시점에 실행)
    unlockAudio();

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/auth/verify', {
        phone: phone.replace(/-/g, ''),
        birth_date: birthDate
      });

      const authResult = response.data;

      // 세션 스토리지에 인증 정보 저장
      sessionStorage.setItem('authResult', JSON.stringify(authResult));
      sessionStorage.setItem('sessionId', authResult.session_id);

      // 음성 상담 페이지로 이동
      navigate('/consultation');
    } catch (err) {
      console.error('Auth error:', err);
      setError(
        err.response?.data?.detail ||
        '인증 처리 중 오류가 발생했습니다. 다시 시도해주세요.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <AuthCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Logo>
          <LogoText>KT AI 상담</LogoText>
          <LogoSubtext>스마트한 요금제 상담 서비스</LogoSubtext>
        </Logo>

        <Title>본인 확인</Title>
        <Subtitle>
          상담을 시작하기 전에 본인 확인이 필요합니다.<br />
          전화번호와 생년월일을 입력해주세요.
        </Subtitle>

        <Form onSubmit={handleSubmit}>
          <PhoneInput value={phone} onChange={setPhone} />
          <BirthDateInput value={birthDate} onChange={setBirthDate} />

          {error && <ErrorMessage>{error}</ErrorMessage>}

          <SubmitButton type="submit" disabled={!isValid || loading}>
            {loading ? '확인 중...' : '상담 시작하기'}
          </SubmitButton>
        </Form>

        <InfoBox>
          <InfoTitle>테스트 계정</InfoTitle>
          <InfoText>
            • Y요금제 대상: 010-1234-5678 / 1995.03.15<br />
            • 시니어 대상: 010-9876-5432 / 1955.07.22<br />
            • 일반 고객: 010-1111-2222 / 1980.05.15<br />
            • 타사 고객: 아무 번호 / 아무 생년월일
          </InfoText>
        </InfoBox>
      </AuthCard>
    </PageContainer>
  );
};

export default CustomerAuthPage;
