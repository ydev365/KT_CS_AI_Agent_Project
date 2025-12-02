import React from 'react';
import styled from 'styled-components';
import { FiUser, FiBell, FiSettings, FiLogOut, FiCheckCircle, FiAlertTriangle, FiCpu } from 'react-icons/fi';
import { motion } from 'framer-motion';

const HeaderContainer = styled.header`
  background: white;
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 100;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const LogoText = styled.h1`
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const LogoSubtext = styled.span`
  font-size: 0.9rem;
  color: #666;
  font-weight: 400;
`;

const CenterStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const StatusCard = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: ${props => {
    switch(props.type) {
      case 'ai-complete': return 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
      case 'waiting': return 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
      case 'in-progress': return 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
      default: return '#f3f4f6';
    }
  }};
  color: white;
  border-radius: 30px;
  font-size: 0.9rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
`;

const StatusIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
`;

const StatusText = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
`;

const StatusLabel = styled.span`
  font-size: 0.75rem;
  opacity: 0.9;
`;

const StatusValue = styled.span`
  font-size: 0.95rem;
  font-weight: 600;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const NotificationButton = styled.button`
  position: relative;
  background: transparent;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  
  &:hover {
    background: #f0f0f0;
    color: #333;
  }
  
  svg {
    font-size: 1.3rem;
  }
`;

const NotificationBadge = styled.span`
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse 2s infinite;
  
  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }
  }
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #f9f9f9;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f0f0f0;
  }
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
`;

const UserName = styled.span`
  font-size: 0.9rem;
  color: #333;
  font-weight: 500;
`;

const IconButton = styled.button`
  background: transparent;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  
  &:hover {
    background: #f0f0f0;
    color: #333;
  }
  
  svg {
    font-size: 1.3rem;
  }
`;

const Header = () => {
  return (
    <HeaderContainer>
      <Logo>
        <LogoText>KT CS Assistant</LogoText>
        <LogoSubtext>AI 상담 도우미</LogoSubtext>
      </Logo>

      <CenterStatus>
        <StatusCard
          type="ai-complete"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <StatusIcon>
            <FiCpu />
          </StatusIcon>
          <StatusText>
            <StatusLabel>AI 상담 상태</StatusLabel>
            <StatusValue>완료됨</StatusValue>
          </StatusText>
        </StatusCard>

        <StatusCard
          type="waiting"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <StatusIcon>
            <FiAlertTriangle />
          </StatusIcon>
          <StatusText>
            <StatusLabel>후속 처리</StatusLabel>
            <StatusValue>대기 중</StatusValue>
          </StatusText>
        </StatusCard>
      </CenterStatus>

      <RightSection>
        <NotificationButton>
          <FiBell />
          <NotificationBadge />
        </NotificationButton>
        
        <IconButton>
          <FiSettings />
        </IconButton>
        
        <UserInfo>
          <UserAvatar>
            <FiUser />
          </UserAvatar>
          <UserName>상담사 김철수</UserName>
        </UserInfo>
        
        <IconButton>
          <FiLogOut />
        </IconButton>
      </RightSection>
    </HeaderContainer>
  );
};

export default Header;
