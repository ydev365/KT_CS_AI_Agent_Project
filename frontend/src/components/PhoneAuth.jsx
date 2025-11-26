import React, { useState } from 'react';
import { verifyCustomer } from '../services/api';

function PhoneAuth({ onAuth, onShowHistory }) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const formatPhoneNumber = (value) => {
    const numbers = value.replace(/[^\d]/g, '');
    if (numbers.length <= 3) return numbers;
    if (numbers.length <= 7) return `${numbers.slice(0, 3)}-${numbers.slice(3)}`;
    return `${numbers.slice(0, 3)}-${numbers.slice(3, 7)}-${numbers.slice(7, 11)}`;
  };

  const handleChange = (e) => {
    const formatted = formatPhoneNumber(e.target.value);
    setPhoneNumber(formatted);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const cleanNumber = phoneNumber.replace(/-/g, '');

    if (cleanNumber.length !== 11) {
      setError('올바른 전화번호를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await verifyCustomer(cleanNumber);
      onAuth(response);
    } catch (err) {
      setError('인증 중 오류가 발생했습니다. 다시 시도해주세요.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="phone-auth">
      <div className="logo">
        <h2>KT AI 상담원</h2>
        <p>요금제 상담 서비스</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="phone">전화번호를 입력해주세요</label>
          <input
            id="phone"
            type="tel"
            placeholder="010-0000-0000"
            value={phoneNumber}
            onChange={handleChange}
            maxLength={13}
            autoComplete="tel"
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? '확인 중...' : '상담 시작'}
        </button>
      </form>

      <div className="history-link">
        <button type="button" onClick={onShowHistory}>
          이전 상담 내역 보기
        </button>
      </div>
    </div>
  );
}

export default PhoneAuth;
