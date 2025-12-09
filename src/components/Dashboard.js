import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import AIConversationLog from './AIConversationLog';
import AISummaryPanel from './AISummaryPanel';
import CustomerInfoPanel from './CustomerInfoPanel';
import QuickSearchPanel from './QuickSearchPanel';
import ConsultationHistory from './ConsultationHistory';
import Header from './Header';
import { motion } from 'framer-motion';
import { consultationApi, customerApi, planApi } from '../services/api';
import socketService from '../services/socket';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr 1.2fr;
  gap: 20px;
  padding: 20px;
  height: calc(100vh - 70px);

  @media (max-width: 1400px) {
    grid-template-columns: 320px 1fr 380px;
  }

  @media (max-width: 1200px) {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
  }
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 300px;
`;

const CenterPanel = styled.div`
  display: flex;
  flex-direction: column;
  min-width: 400px;
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 350px;
`;

// 생년월일 포맷 변환 (YYYYMMDD → YYYY-MM-DD)
const formatBirthDate = (birthDate) => {
  if (!birthDate) return null;
  if (birthDate.includes('-')) return birthDate;
  return `${birthDate.slice(0, 4)}-${birthDate.slice(4, 6)}-${birthDate.slice(6, 8)}`;
};

// 고객 유형별 이전 상담 내역 더미 데이터
const CONSULTATION_HISTORY_BY_TYPE = {
  // Y요금제 대상 (만 34세 이하)
  'Y': [
    {
      id: 'Y001',
      date: '2024-11-20 15:30',
      summary: '넷플릭스 부가서비스 추가 문의',
      status: 'resolved',
      tags: ['OTT', '넷플릭스', '부가서비스'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, KT AI 상담사입니다. 무엇을 도와드릴까요?', timestamp: '15:30:10' },
        { speaker: 'customer', content: '넷플릭스 추가하고 싶은데요', timestamp: '15:30:25' },
        { speaker: 'ai', content: '네, 현재 5G 슬림 14GB 요금제에 넷플릭스 부가서비스 추가 가능해요. 넷플릭스 스탠다드가 12,500원인데, 직접 구독보다 천원 저렴해요.', timestamp: '15:30:40' },
        { speaker: 'customer', content: '오 그럼 추가해주세요', timestamp: '15:30:55' },
      ],
      aiSummary: {
        currentPlan: '5G 슬림 14GB',
        requestedFeature: '넷플릭스 부가서비스',
        mainConcern: 'OTT 저렴하게 이용',
        result: '넷플릭스 스탠다드 부가서비스 추가 완료'
      }
    },
    {
      id: 'Y002',
      date: '2024-10-05 11:20',
      summary: 'Y 프로모션 혜택 문의',
      status: 'resolved',
      tags: ['Y요금제', '프로모션', '혜택'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, 무엇을 도와드릴까요?', timestamp: '11:20:10' },
        { speaker: 'customer', content: 'Y요금제 쓰면 뭐가 좋아요?', timestamp: '11:20:25' },
        { speaker: 'ai', content: 'Y요금제는 만 34세 이하 고객님을 위한 요금제로, 데이터 혜택과 함께 다양한 제휴 할인이 있어요. 스타벅스, 배달의민족 할인 등 받으실 수 있습니다.', timestamp: '11:20:45' },
      ],
      aiSummary: {
        currentPlan: '5G 슬림 14GB',
        requestedFeature: 'Y 프로모션 혜택 확인',
        mainConcern: '청년 혜택 활용',
        result: 'Y 프로모션 혜택 안내 완료'
      }
    }
  ],

  // 시니어 대상 (만 65세 이상)
  '시니어': [
    {
      id: 'S001',
      date: '2024-11-18 10:00',
      summary: '요금제 단순화 요청',
      status: 'resolved',
      tags: ['시니어', '요금 절약', '단순화'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, KT AI 상담사입니다. 무엇을 도와드릴까요?', timestamp: '10:00:10' },
        { speaker: 'customer', content: '요금이 너무 복잡해요. 좀 단순한 걸로 바꿀 수 있나요?', timestamp: '10:00:30' },
        { speaker: 'ai', content: '네, 시니어 고객님을 위한 간편한 요금제가 있어요. 5G 시니어 베이직은 월 49,000원이고, 데이터 10GB에 통화 무제한이에요.', timestamp: '10:00:50' },
        { speaker: 'customer', content: '그게 좋겠네요', timestamp: '10:01:10' },
      ],
      aiSummary: {
        currentPlan: '5G 베이직',
        requestedFeature: '간편한 요금제',
        mainConcern: '복잡한 요금 체계',
        result: '5G 시니어 베이직 변경 완료'
      }
    },
    {
      id: 'S002',
      date: '2024-09-25 14:30',
      summary: '가족 데이터 쉐어링 문의',
      status: 'resolved',
      tags: ['가족', '데이터 쉐어링'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, 무엇을 도와드릴까요?', timestamp: '14:30:10' },
        { speaker: 'customer', content: '손주한테 데이터 나눠줄 수 있나요?', timestamp: '14:30:25' },
        { speaker: 'ai', content: '네, 가족 데이터 쉐어링 서비스로 가능해요. 월 2,200원에 가족에게 데이터를 나눠주실 수 있습니다.', timestamp: '14:30:45' },
      ],
      aiSummary: {
        currentPlan: '5G 시니어 베이직',
        requestedFeature: '데이터 쉐어링',
        mainConcern: '가족과 데이터 공유',
        result: '데이터 쉐어링 서비스 안내 완료'
      }
    }
  ],

  // 일반 고객 (35~64세)
  '일반': [
    {
      id: 'G001',
      date: '2024-11-22 16:45',
      summary: 'OTT 결합 상품 문의',
      status: 'resolved',
      tags: ['OTT', '결합상품', '넷플릭스'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, KT AI 상담사입니다. 무엇을 도와드릴까요?', timestamp: '16:45:10' },
        { speaker: 'customer', content: '넷플릭스랑 요금제 같이 쓰면 할인 되나요?', timestamp: '16:45:25' },
        { speaker: 'ai', content: '네, 5G 초이스 베이직 요금제에는 넷플릭스가 포함되어 있어요. 월 90,000원이고 선택약정하면 67,500원에 이용 가능합니다.', timestamp: '16:45:45' },
        { speaker: 'customer', content: '기존 요금제에 부가서비스로만 추가할 수는 없나요?', timestamp: '16:46:00' },
        { speaker: 'ai', content: '물론 가능해요! 현재 요금제에 넷플릭스 스탠다드 부가서비스를 12,500원에 추가하실 수 있어요.', timestamp: '16:46:20' },
      ],
      aiSummary: {
        currentPlan: '5G 베이직',
        requestedFeature: 'OTT 결합',
        mainConcern: '넷플릭스 저렴하게 이용',
        result: '넷플릭스 부가서비스 추가 완료'
      }
    },
    {
      id: 'G002',
      date: '2024-10-10 09:30',
      summary: '가족 결합 할인 문의',
      status: 'resolved',
      tags: ['가족결합', '할인'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, 무엇을 도와드릴까요?', timestamp: '09:30:10' },
        { speaker: 'customer', content: '가족이 4명인데 다 같이 KT 쓰면 할인 얼마나 되나요?', timestamp: '09:30:25' },
        { speaker: 'ai', content: '4명이시면 온가족 할인으로 1인당 월 최대 20% 할인 받으실 수 있어요. 인터넷까지 결합하시면 추가 할인도 있습니다.', timestamp: '09:30:50' },
      ],
      aiSummary: {
        currentPlan: '5G 베이직',
        requestedFeature: '가족 결합 할인',
        mainConcern: '가족 요금 절감',
        result: '온가족 결합 할인 안내 완료'
      }
    },
    {
      id: 'G003',
      date: '2024-09-15 11:00',
      summary: '인터넷 결합 상품 가입',
      status: 'resolved',
      tags: ['인터넷', '결합상품'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, KT AI 상담사입니다.', timestamp: '11:00:10' },
        { speaker: 'customer', content: '인터넷이랑 휴대폰 같이 쓰면 할인 되나요?', timestamp: '11:00:25' },
        { speaker: 'ai', content: '네, KT 기가인터넷과 모바일 결합 시 월 최대 16,500원 할인 가능합니다.', timestamp: '11:00:40' },
      ],
      aiSummary: {
        currentPlan: '5G 베이직',
        requestedFeature: '인터넷 결합',
        mainConcern: '결합 할인 혜택',
        result: '기가인터넷 결합 안내 완료'
      }
    }
  ],

  // Y틴 대상 (만 18세 이하)
  'Y틴': [
    {
      id: 'T001',
      date: '2024-11-15 17:00',
      summary: '데이터 추가 요청',
      status: 'resolved',
      tags: ['데이터', 'Y틴', '추가'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, KT AI 상담사입니다. 무엇을 도와드릴까요?', timestamp: '17:00:10' },
        { speaker: 'customer', content: '데이터가 부족해요 더 추가할 수 있나요?', timestamp: '17:00:25' },
        { speaker: 'ai', content: '현재 Y틴 요금제 사용 중이시네요. 데이터 1GB 추가는 1,100원, 무제한 데이터 충전은 3,300원에 가능해요.', timestamp: '17:00:45' },
        { speaker: 'customer', content: '무제한으로 해주세요', timestamp: '17:01:00' },
      ],
      aiSummary: {
        currentPlan: '5G Y틴',
        requestedFeature: '데이터 추가',
        mainConcern: '데이터 부족',
        result: '무제한 데이터 충전 완료'
      }
    },
    {
      id: 'T002',
      date: '2024-10-20 19:30',
      summary: '유튜브 프리미엄 문의',
      status: 'resolved',
      tags: ['유튜브', 'OTT', '부가서비스'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, 무엇을 도와드릴까요?', timestamp: '19:30:10' },
        { speaker: 'customer', content: '유튜브 프리미엄 추가할 수 있어요?', timestamp: '19:30:25' },
        { speaker: 'ai', content: '네, 유튜브 프리미엄 부가서비스를 13,900원에 추가하실 수 있어요. 광고 없이 유튜브 보실 수 있고, 유튜브 뮤직도 무료로 이용 가능해요.', timestamp: '19:30:50' },
      ],
      aiSummary: {
        currentPlan: '5G Y틴',
        requestedFeature: '유튜브 프리미엄',
        mainConcern: '유튜브 광고 없이 보기',
        result: '유튜브 프리미엄 부가서비스 안내 완료'
      }
    }
  ]
};

// 고객 유형에 따른 상담 내역 반환
const getConsultationHistoryByType = (primaryTarget) => {
  if (primaryTarget?.includes('34세')) return CONSULTATION_HISTORY_BY_TYPE['Y'];
  if (primaryTarget?.includes('65세')) return CONSULTATION_HISTORY_BY_TYPE['시니어'];
  if (primaryTarget?.includes('18세')) return CONSULTATION_HISTORY_BY_TYPE['Y틴'];
  return CONSULTATION_HISTORY_BY_TYPE['일반'];
};

const Dashboard = () => {
  const [conversationLog, setConversationLog] = useState([]);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [customerInfo, setCustomerInfo] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [consultationHistory, setConsultationHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 현재 상담 ID (실제로는 라우터 파라미터나 컨텍스트에서 받아옴)
  const consultationId = 'CONS001';
  const customerId = 'C001';

  // API에서 데이터 로드
  const loadDataFromAPI = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // 병렬로 API 호출
      const [consultationRes, customerRes] = await Promise.all([
        consultationApi.getConsultation(consultationId),
        customerApi.getCustomer(customerId)
      ]);

      // 상담 데이터 설정
      const { consultation, conversation } = consultationRes.data;
      setConversationLog(conversation.messages);
      setAiAnalysis(consultation);

      // 고객 정보 설정
      setCustomerInfo(customerRes.data);

    } catch (err) {
      console.error('Failed to load data from API:', err);
      setError('데이터를 불러오는데 실패했습니다. 샘플 데이터를 표시합니다.');
      // API 실패 시 샘플 데이터로 폴백
      loadSampleData();
    } finally {
      setLoading(false);
    }
  }, []);

  // 샘플 데이터 (API 실패 시 폴백)
  const loadSampleData = () => {
    setConversationLog([
      {
        timestamp: '2024-11-19T03:50:10',
        speaker: 'ai',
        speakerId: 'AI 상담사',
        content: '안녕하세요, KT 고객센터입니다. 무엇을 도와드릴까요?'
      },
      {
        timestamp: '2024-11-19T03:50:15',
        speaker: 'customer',
        speakerId: '고객_010-1234-5678',
        content: '안녕하세요, 요금제 변경하고 싶은데요.'
      },
      {
        timestamp: '2024-11-19T03:50:25',
        speaker: 'ai',
        speakerId: 'AI 상담사',
        content: '네, 요금제 변경을 도와드리겠습니다. 현재 사용 중이신 요금제는 5G 베이직 플랜이시며, 월 55,000원입니다. 어떤 요금제를 찾고 계신가요?'
      },
      {
        timestamp: '2024-11-19T03:50:35',
        speaker: 'customer',
        speakerId: '고객_010-1234-5678',
        content: '데이터를 더 많이 쓸 수 있는 요금제로 바꾸고 싶어요. 한 달에 100GB 정도는 필요할 것 같아요.'
      },
      {
        timestamp: '2024-11-19T03:50:50',
        speaker: 'ai',
        speakerId: 'AI 상담사',
        content: '5G 슈퍼플랜은 월 69,000원으로 150GB를 제공합니다. 가족 결합하시면 더 저렴하게 이용 가능합니다.'
      },
      {
        timestamp: '2024-11-19T03:51:05',
        speaker: 'customer',
        speakerId: '고객_010-1234-5678',
        content: '좋아요. 그런데 가족 결합 할인도 되나요? 아내랑 아들도 KT 써요.'
      },
      {
        timestamp: '2024-11-19T03:51:20',
        speaker: 'ai',
        speakerId: 'AI 상담사',
        content: '네, 3명 결합 시 20% 할인되어 월 55,200원에 이용 가능합니다.'
      }
    ]);

    setAiAnalysis({
      summary: {
        currentPlan: '5G 베이직',
        currentPrice: 55000,
        requestedFeature: '더 많은 데이터 (100GB+)',
        customerProfile: '가족 3명 KT 이용 중',
        mainConcern: '데이터 부족',
        opportunity: '가족 결합 할인 가능'
      },
      recommendedPlans: [
        {
          id: 1,
          name: '5G 슈퍼플랜',
          price: 69000,
          discountedPrice: 55200,
          discount: '가족 3명 20%',
          data: '150GB',
          features: ['5G 무제한 속도', '150GB 데이터', '음성/문자 무제한', '로밍 데이터 3GB'],
          badge: 'best',
          comparison: '현재 요금과 비슷한 가격에 3배 데이터'
        },
        {
          id: 2,
          name: '5G 프리미엄 언리미티드',
          price: 79000,
          discountedPrice: 63200,
          discount: '가족 3명 20%',
          data: '무제한',
          features: ['5G 무제한 속도', '데이터 완전 무제한', '음성/문자 무제한', '프리미엄 혜택'],
          badge: 'upsell',
          comparison: '월 8,000원 추가로 완전 무제한'
        },
        {
          id: 3,
          name: '5G 스탠다드',
          price: 59000,
          discountedPrice: 47200,
          discount: '가족 3명 20%',
          data: '80GB',
          features: ['5G 무제한 속도', '80GB 데이터', '음성/문자 무제한'],
          badge: 'budget',
          comparison: '월 8,000원 절약, 데이터 80GB'
        }
      ]
    });

    setCustomerInfo({
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
    });

    // 샘플 이전 상담 내역
    setConsultationHistory([
      {
        id: 'H001',
        date: '2024-11-15 14:30',
        summary: '데이터 요금제 변경 문의',
        status: 'resolved',
        tags: ['요금제 변경', '5G'],
        conversation: [
          { speaker: 'ai', content: '안녕하세요, KT 고객센터입니다.', timestamp: '14:30:10' },
          { speaker: 'customer', content: '요금제 변경하고 싶어요', timestamp: '14:30:25' },
          { speaker: 'ai', content: '네, 어떤 요금제를 원하시나요?', timestamp: '14:30:35' },
        ],
        aiSummary: {
          currentPlan: '5G 베이직',
          requestedFeature: '데이터 증량',
          mainConcern: '데이터 부족',
          result: '5G 슈퍼플랜 안내 완료'
        }
      },
      {
        id: 'H002',
        date: '2024-11-10 10:15',
        summary: '인터넷 결합 할인 문의',
        status: 'resolved',
        tags: ['결합할인', '인터넷'],
        conversation: [
          { speaker: 'ai', content: '안녕하세요, 무엇을 도와드릴까요?', timestamp: '10:15:10' },
          { speaker: 'customer', content: '인터넷이랑 결합하면 할인되나요?', timestamp: '10:15:30' },
        ],
        aiSummary: {
          currentPlan: '5G 베이직',
          requestedFeature: '결합 할인',
          mainConcern: '요금 절감',
          result: '결합 할인 안내 완료'
        }
      }
    ]);
  };

  // sessionStorage에서 상담 결과 로드
  const loadFromSessionStorage = useCallback(() => {
    const consultationResult = sessionStorage.getItem('consultationResult');
    const authResult = sessionStorage.getItem('authResult');

    if (consultationResult) {
      try {
        const data = JSON.parse(consultationResult);
        console.log('Loaded consultation result:', data);

        // 대화 로그 설정
        if (data.conversation && data.conversation.length > 0) {
          const formattedConversation = data.conversation.map((msg, idx) => ({
            timestamp: msg.timestamp,
            speaker: msg.speaker,
            speakerId: msg.speaker === 'ai' ? 'AI 상담사' : '고객',
            content: msg.content
          }));
          setConversationLog(formattedConversation);
        }

        // AI 분석 설정 (백엔드 형식 → 프론트엔드 형식 변환)
        if (data.summary || data.recommendations) {
          // recommendations 배열을 프론트엔드 형식으로 변환
          const normalizedRecommendations = (data.recommendations || []).map(rec => ({
            id: rec.id,
            name: rec.name,
            price: rec.price,
            discountedPrice: rec.discounted_price || rec.price,
            discount: rec.discount || '할인 없음',
            data: rec.data,
            features: rec.features || [],
            badge: rec.badge,
            comparison: rec.comparison,
            score: rec.score,
            scoreBreakdown: rec.score_breakdown
          }));

          setAiAnalysis({
            summary: data.summary,
            recommendedPlans: normalizedRecommendations
          });
        }

        // 고객 정보 설정 (백엔드 형식 → 프론트엔드 형식 변환)
        if (data.customerInfo) {
          const ci = data.customerInfo;
          setCustomerInfo({
            name: ci.name,
            phone: ci.phone,
            gender: ci.gender || '정보 없음',
            birthDate: ci.birth_date ? formatBirthDate(ci.birth_date) : null,
            age: ci.age,
            isKtMember: ci.is_kt_customer,
            membershipGrade: ci.membership_grade || (ci.is_kt_customer ? '일반' : '타사 고객'),
            ktJoinDate: ci.kt_join_date,
            currentPlan: ci.current_plan,
            currentPlanStartDate: ci.kt_join_date, // 가입일로 대체
            monthlyFee: ci.monthly_fee || 0,
            services: ci.services || [],
            totalMonthlyFee: ci.total_monthly_fee || ci.monthly_fee || 0,
            loyaltyYears: ci.loyalty_years || 0,
            familyMembers: ci.family_members || 1
          });
        }

        // 이전 상담 내역 더미 데이터 설정 (KT 고객만, 유형별)
        if (data.customerInfo?.is_kt_customer) {
          setConsultationHistory(getConsultationHistoryByType(data.customerInfo.primary_target));
        } else {
          setConsultationHistory([]);
        }

        setLoading(false);
        return true;
      } catch (e) {
        console.error('Failed to parse consultation result:', e);
      }
    }

    // authResult에서 고객 정보만이라도 로드
    if (authResult) {
      try {
        const auth = JSON.parse(authResult);
        if (auth.customer) {
          const ci = auth.customer;
          setCustomerInfo({
            name: ci.name,
            phone: ci.phone,
            gender: ci.gender || '정보 없음',
            birthDate: ci.birth_date ? formatBirthDate(ci.birth_date) : null,
            age: ci.age,
            isKtMember: ci.is_kt_customer,
            membershipGrade: ci.membership_grade || (ci.is_kt_customer ? '일반' : '타사 고객'),
            ktJoinDate: ci.kt_join_date,
            currentPlan: ci.current_plan,
            currentPlanStartDate: ci.kt_join_date,
            monthlyFee: ci.monthly_fee || 0,
            services: ci.services || [],
            totalMonthlyFee: ci.total_monthly_fee || ci.monthly_fee || 0,
            loyaltyYears: ci.loyalty_years || 0,
            familyMembers: ci.family_members || 1
          });
          // 이전 상담 내역 더미 데이터 설정 (KT 고객만, 유형별)
          if (ci.is_kt_customer) {
            setConsultationHistory(getConsultationHistoryByType(ci.primary_target));
          } else {
            setConsultationHistory([]);
          }
        }
      } catch (e) {
        console.error('Failed to parse auth result:', e);
      }
    }

    return false;
  }, []);

  useEffect(() => {
    // sessionStorage에서 먼저 로드 시도
    const loadedFromStorage = loadFromSessionStorage();

    if (!loadedFromStorage) {
      // sessionStorage에 데이터가 없으면 API에서 로드 시도
      loadDataFromAPI();
    }

    // WebSocket 연결
    const socket = socketService.connect();

    if (socket) {
      // 상담 세션 참가
      socketService.joinConsultation(consultationId);

      // 실시간 이벤트 리스너 설정
      socketService.onConsultationUpdate((data) => {
        console.log('Consultation updated:', data);
        // 상담 데이터 갱신
        if (data.conversation) {
          setConversationLog(data.conversation.messages);
        }
        if (data.analysis) {
          setAiAnalysis(data.analysis);
        }
      });

      socketService.onNewMessage((message) => {
        console.log('New message:', message);
        setConversationLog(prev => [...prev, message]);
      });

      socketService.onStatusChange((data) => {
        console.log('Status changed:', data);
      });

      // 상담 완료 이벤트 수신
      socket.on('consultation:completed', (data) => {
        console.log('Consultation completed:', data);
        // 대화 로그 업데이트
        if (data.conversation) {
          const formattedConversation = data.conversation.map((msg) => ({
            timestamp: msg.timestamp,
            speaker: msg.speaker,
            speakerId: msg.speaker === 'ai' ? 'AI 상담사' : '고객',
            content: msg.content
          }));
          setConversationLog(formattedConversation);
        }
        // AI 분석 업데이트 (백엔드 snake_case → 프론트엔드 camelCase 변환)
        if (data.summary && data.recommendations) {
          const normalizedRecommendations = data.recommendations.map(rec => ({
            id: rec.id,
            name: rec.name,
            price: rec.price,
            discountedPrice: rec.discounted_price || rec.price,
            discount: rec.discount || '할인 없음',
            data: rec.data,
            features: rec.features || [],
            badge: rec.badge,
            comparison: rec.comparison,
            score: rec.score,
            scoreBreakdown: rec.score_breakdown
          }));
          setAiAnalysis({
            summary: data.summary,
            recommendedPlans: normalizedRecommendations
          });
        }
        // 고객 정보 업데이트
        if (data.customerInfo) {
          setCustomerInfo(prev => ({ ...prev, ...data.customerInfo }));
        }
      });
    }

    // 클린업
    return () => {
      socketService.leaveConsultation(consultationId);
      socketService.removeAllListeners();
    };
  }, [loadDataFromAPI, loadFromSessionStorage]);

  const handleSearch = async (query, filters = []) => {
    console.log('[Dashboard] Searching plans:', { query, filters });
    try {
      const response = await planApi.searchPlans({
        query: query || undefined,  // null이면 undefined로 변환
        filters,
        pageSize: 100  // 전체 결과 가져오기
      });
      console.log('[Dashboard] Search results:', response.data);
      setSearchResults(response.data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
      // 검색 실패 시 빈 결과
      setSearchResults([]);
    }
  };

  return (
    <DashboardContainer>
      <Header />

      <MainContent>
        {/* 좌측: 고객 정보 + 이전 상담 내역 */}
        <LeftPanel>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            style={{ flex: '0 0 auto' }}
          >
            <CustomerInfoPanel customerInfo={customerInfo} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            style={{ flex: '1', minHeight: 0 }}
          >
            <ConsultationHistory
              customerId={customerId}
              history={consultationHistory}
            />
          </motion.div>
        </LeftPanel>

        {/* 중앙: 대화 로그 */}
        <CenterPanel>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{ flex: 1 }}
          >
            <AIConversationLog conversationLog={conversationLog} />
          </motion.div>
        </CenterPanel>

        {/* 우측: AI 요약/추천 + 요금제 검색 */}
        <RightPanel>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            style={{ flex: '0 0 auto' }}
          >
            <AISummaryPanel aiAnalysis={aiAnalysis} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            style={{ flex: '1 1 auto', minHeight: '150px', overflow: 'auto' }}
          >
            <QuickSearchPanel
              onSearch={handleSearch}
              searchResults={searchResults}
            />
          </motion.div>
        </RightPanel>
      </MainContent>
    </DashboardContainer>
  );
};

export default Dashboard;
