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

const BirthDateInput = ({ value, onChange }) => {
  const formatBirthDate = (input) => {
    // 숫자만 추출
    const numbers = input.replace(/\D/g, '');

    // 8자리까지만
    const limited = numbers.slice(0, 8);

    // 자동 점 추가
    if (limited.length <= 4) {
      return limited;
    } else if (limited.length <= 6) {
      return `${limited.slice(0, 4)}.${limited.slice(4)}`;
    } else {
      return `${limited.slice(0, 4)}.${limited.slice(4, 6)}.${limited.slice(6)}`;
    }
  };

  const handleChange = (e) => {
    const input = e.target.value;
    const numbers = input.replace(/\D/g, '').slice(0, 8);
    onChange(numbers);
  };

  const displayValue = formatBirthDate(value);

  return (
    <InputGroup>
      <Label>생년월일</Label>
      <Input
        type="text"
        placeholder="1990.01.01"
        value={displayValue}
        onChange={handleChange}
        maxLength={10}
      />
      <HelpText>8자리 숫자로 입력해주세요 (예: 19900101)</HelpText>
    </InputGroup>
  );
};

export default BirthDateInput;
