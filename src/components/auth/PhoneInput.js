import React from 'react';
import styled from 'styled-components';

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: #333;
`;

const Input = styled.input`
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 18px;
  letter-spacing: 2px;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #a0aec0;
    letter-spacing: 0;
  }
`;

const HelpText = styled.span`
  font-size: 12px;
  color: #718096;
`;

const PhoneInput = ({ value, onChange }) => {
  const formatPhone = (input) => {
    // 숫자만 추출
    const numbers = input.replace(/\D/g, '');

    // 11자리까지만
    const limited = numbers.slice(0, 11);

    // 자동 하이픈 추가
    if (limited.length <= 3) {
      return limited;
    } else if (limited.length <= 7) {
      return `${limited.slice(0, 3)}-${limited.slice(3)}`;
    } else {
      return `${limited.slice(0, 3)}-${limited.slice(3, 7)}-${limited.slice(7)}`;
    }
  };

  const handleChange = (e) => {
    const formatted = formatPhone(e.target.value);
    onChange(formatted.replace(/-/g, ''));
  };

  const displayValue = formatPhone(value);

  return (
    <InputGroup>
      <Label>전화번호</Label>
      <Input
        type="tel"
        placeholder="010-0000-0000"
        value={displayValue}
        onChange={handleChange}
        maxLength={13}
      />
      <HelpText>휴대폰 번호를 입력해주세요</HelpText>
    </InputGroup>
  );
};

export default PhoneInput;
