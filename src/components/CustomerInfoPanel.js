import React from 'react';
import styled from 'styled-components';
import { FiUser, FiUsers, FiPhone, FiCalendar, FiPackage, FiWifi, FiTv, FiSmartphone, FiClock, FiAward, FiTrendingUp } from 'react-icons/fi';
import { motion } from 'framer-motion';

const PanelContainer = styled(motion.div)`
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`;

const PanelHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
`;

const Title = styled.h3`
  font-size: 1.1rem;
  color: #333;
  font-weight: 600;
`;

const CustomerAvatar = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: ${props => props.isVip ? 
    'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)' : 
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  };
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
  font-size: 2rem;
  position: relative;
`;

const VipBadge = styled.div`
  position: absolute;
  top: -5px;
  right: -5px;
  background: #f59e0b;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  border: 2px solid white;
`;

const CustomerName = styled.h2`
  text-align: center;
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 4px;
  font-weight: 700;
`;

const CustomerPhone = styled.p`
  text-align: center;
  color: #666;
  font-size: 0.95rem;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
`;

const InfoSection = styled.div`
  margin-bottom: 20px;
`;

const SectionTitle = styled.h4`
  font-size: 0.85rem;
  color: #999;
  text-transform: uppercase;
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
`;

const InfoItem = styled.div`
  padding: 10px;
  background: #f9fafb;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid #e5e7eb;
  
  &:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
  }
`;

const InfoLabel = styled.span`
  font-size: 0.75rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 4px;
  
  svg {
    font-size: 0.9rem;
  }
`;

const InfoValue = styled.span`
  font-size: 0.9rem;
  color: #1f2937;
  font-weight: 600;
`;

const ServiceSection = styled.div`
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
`;

const CurrentPlan = styled.div`
  background: white;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  border: 1px solid #bfdbfe;
`;

const PlanName = styled.div`
  font-size: 1rem;
  color: #1e40af;
  font-weight: 700;
  margin-bottom: 4px;
`;

const PlanDetails = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #64748b;
`;

const ServiceList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
`;

const ServiceBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: ${props => {
    switch(props.type) {
      case 'mobile': return '#667eea';
      case 'internet': return '#764ba2';
      case 'tv': return '#f59e0b';
      case 'bundle': return '#10b981';
      default: return '#94a3b8';
    }
  }};
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
`;

const MembershipInfo = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: #fef3c7;
  border-radius: 8px;
  margin-bottom: 12px;
`;

const MembershipLabel = styled.span`
  font-size: 0.85rem;
  color: #92400e;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const MembershipValue = styled.span`
  font-size: 0.85rem;
  color: #92400e;
  font-weight: 700;
`;

const CustomerInfoPanel = ({ customerInfo }) => {
  // 샘플 데이터 (실제로는 props로 받아옴)
  const customer = customerInfo || {
    name: '김철수',
    phone: '010-1234-5678',
    gender: '남성',
    birthDate: '1985-03-15',
    age: 39,
    isKtMember: true,
    membershipGrade: 'VIP',
    ktJoinDate: '2015-06-20',
    currentPlan: '5G 베이직',
    currentPlanStartDate: '2023-01-15',
    monthlyFee: 55000,
    services: [
      { type: 'mobile', name: '5G 모바일' },
      { type: 'internet', name: '기가인터넷' },
      { type: 'tv', name: 'IPTV' }
    ],
    totalMonthlyFee: 125000,
    loyaltyYears: 9,
    familyMembers: 3
  };

  const calculateAge = (birthDate) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const calculateDuration = (startDate) => {
    const start = new Date(startDate);
    const now = new Date();
    const years = now.getFullYear() - start.getFullYear();
    const months = now.getMonth() - start.getMonth();
    const totalMonths = years * 12 + months;
    
    if (years > 0) {
      return `${years}년 ${months}개월`;
    } else {
      return `${totalMonths}개월`;
    }
  };

  const getServiceIcon = (type) => {
    switch(type) {
      case 'mobile': return <FiSmartphone />;
      case 'internet': return <FiWifi />;
      case 'tv': return <FiTv />;
      case 'bundle': return <FiPackage />;
      default: return null;
    }
  };

  return (
    <PanelContainer
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <PanelHeader>
        <FiUser />
        <Title>고객 정보</Title>
      </PanelHeader>

      <CustomerAvatar isVip={customer.membershipGrade === 'VIP'}>
        <FiUser />
        {customer.membershipGrade === 'VIP' && (
          <VipBadge>
            <FiAward />
          </VipBadge>
        )}
      </CustomerAvatar>
      
      <CustomerName>{customer.name}</CustomerName>
      <CustomerPhone>
        <FiPhone />
        {customer.phone}
      </CustomerPhone>

      <InfoSection>
        <SectionTitle>기본 정보</SectionTitle>
        <InfoGrid>
          <InfoItem>
            <InfoLabel>
              <FiUser />
              성별
            </InfoLabel>
            <InfoValue>{customer.gender}</InfoValue>
          </InfoItem>
          <InfoItem>
            <InfoLabel>
              <FiCalendar />
              나이
            </InfoLabel>
            <InfoValue>{customer.age}세</InfoValue>
          </InfoItem>
          <InfoItem>
            <InfoLabel>
              <FiCalendar />
              생년월일
            </InfoLabel>
            <InfoValue>{formatDate(customer.birthDate)}</InfoValue>
          </InfoItem>
          <InfoItem>
            <InfoLabel>
              <FiAward />
              고객 등급
            </InfoLabel>
            <InfoValue style={{ color: customer.membershipGrade === 'VIP' ? '#f59e0b' : '#667eea' }}>
              {customer.membershipGrade}
            </InfoValue>
          </InfoItem>
        </InfoGrid>
      </InfoSection>

      {customer.isKtMember && (
        <>
          <InfoSection>
            <SectionTitle>KT 가입 정보</SectionTitle>
            <MembershipInfo>
              <MembershipLabel>
                <FiClock />
                KT 이용 기간
              </MembershipLabel>
              <MembershipValue>{customer.loyaltyYears}년차 고객</MembershipValue>
            </MembershipInfo>
            <InfoGrid>
              <InfoItem>
                <InfoLabel>
                  <FiCalendar />
                  가입일
                </InfoLabel>
                <InfoValue>{formatDate(customer.ktJoinDate)}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>
                  <FiUsers />
                  가족 결합
                </InfoLabel>
                <InfoValue>{customer.familyMembers}명</InfoValue>
              </InfoItem>
            </InfoGrid>
          </InfoSection>

          <ServiceSection>
            <SectionTitle>현재 이용 서비스</SectionTitle>
            <CurrentPlan>
              <PlanName>{customer.currentPlan}</PlanName>
              <PlanDetails>
                <span>월 {customer.monthlyFee.toLocaleString()}원</span>
                <span>{calculateDuration(customer.currentPlanStartDate)} 사용</span>
              </PlanDetails>
            </CurrentPlan>
            <ServiceList>
              {customer.services?.map((service, index) => (
                <ServiceBadge key={index} type={service.type}>
                  {getServiceIcon(service.type)}
                  {service.name}
                </ServiceBadge>
              ))}
            </ServiceList>
            <InfoItem style={{ marginTop: '12px', background: 'white' }}>
              <InfoLabel>
                <FiTrendingUp />
                총 월 이용료
              </InfoLabel>
              <InfoValue style={{ fontSize: '1.1rem', color: '#667eea' }}>
                {customer.totalMonthlyFee.toLocaleString()}원
              </InfoValue>
            </InfoItem>
          </ServiceSection>
        </>
      )}
    </PanelContainer>
  );
};

export default CustomerInfoPanel;
