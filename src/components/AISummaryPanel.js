import React from 'react';
import styled from 'styled-components';
import { FiZap, FiTrendingUp, FiPackage, FiDollarSign, FiUsers, FiWifi, FiSmartphone, FiStar } from 'react-icons/fi';
import { motion } from 'framer-motion';

const PanelContainer = styled.div`
  background: white;
  border-radius: 15px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
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

const Title = styled.h2`
  font-size: 1.3rem;
  color: #333;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SummarySection = styled.div`
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
`;

const SectionTitle = styled.h3`
  font-size: 1rem;
  color: #0369a1;
  margin-bottom: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const SummaryText = styled.div`
  font-size: 0.95rem;
  color: #334155;
  line-height: 1.6;
`;

const KeyPoint = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
`;

const KeyPointLabel = styled.span`
  font-weight: 600;
  color: #1e40af;
  font-size: 0.85rem;
  min-width: 80px;
`;

const KeyPointValue = styled.span`
  color: #475569;
  font-size: 0.85rem;
`;

const RecommendationSection = styled.div`
  flex: 1;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
  }
`;

const RecommendationCard = styled(motion.div)`
  background: ${props => props.primary ? 
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 
    'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)'
  };
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  border: ${props => props.primary ? '2px solid #667eea' : '1px solid #e5e7eb'};
`;

const RecommendBadge = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  background: ${props => {
    if (props.type === 'best') return '#10b981';
    if (props.type === 'upsell') return '#f59e0b';
    return '#3b82f6';
  }};
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const PlanName = styled.h4`
  color: ${props => props.primary ? 'white' : '#1f2937'};
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 8px;
`;

const PlanPrice = styled.div`
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
`;

const Price = styled.span`
  color: ${props => props.primary ? 'white' : '#667eea'};
  font-size: 1.3rem;
  font-weight: 700;
`;

const PriceUnit = styled.span`
  color: ${props => props.primary ? 'rgba(255,255,255,0.8)' : '#6b7280'};
  font-size: 0.85rem;
`;

const Discount = styled.span`
  background: #ef4444;
  color: white;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
`;

const PlanFeatures = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 12px;
`;

const Feature = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.primary ? 'rgba(255,255,255,0.95)' : '#4b5563'};
  font-size: 0.85rem;
  
  svg {
    color: ${props => props.primary ? 'white' : '#667eea'};
    flex-shrink: 0;
  }
`;

const ComparisonNote = styled.div`
  background: ${props => props.primary ?
    'rgba(255, 255, 255, 0.2)' :
    'rgba(102, 126, 234, 0.1)'
  };
  border-radius: 8px;
  padding: 10px;
  margin-top: 12px;
  font-size: 0.8rem;
  color: ${props => props.primary ? 'white' : '#4c1d95'};
`;

const ScoreBadge = styled.div`
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: ${props => props.primary ?
    'rgba(255, 255, 255, 0.25)' :
    'rgba(102, 126, 234, 0.15)'
  };
  color: ${props => props.primary ? 'white' : '#667eea'};
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const AISummaryPanel = ({ aiAnalysis }) => {
  // 백엔드 snake_case → 프론트엔드 camelCase 변환
  const normalizeSummary = (summary) => {
    if (!summary) return null;
    return {
      currentPlan: summary.currentPlan || summary.current_plan || '알 수 없음',
      currentPrice: summary.currentPrice || summary.current_price || 0,
      requestedFeature: summary.requestedFeature || summary.requested_feature || '특별한 요청 없음',
      customerProfile: summary.customerProfile || summary.customer_profile || '정보 없음',
      mainConcern: summary.mainConcern || summary.main_concern || '특별한 불만 없음',
      opportunity: summary.opportunity || '추가 확인 필요',
      consultationResult: summary.consultationResult || summary.consultation_result || '상담 진행 중'
    };
  };

  const normalizePlan = (plan) => {
    return {
      id: plan.id,
      name: plan.name,
      price: plan.price || 0,
      discountedPrice: plan.discountedPrice || plan.discounted_price || plan.price || 0,
      discount: plan.discount || '',
      data: plan.data || '',
      features: plan.features || [],
      badge: plan.badge || 'best',
      comparison: plan.comparison || '',
      score: plan.score || null,
      scoreBreakdown: plan.scoreBreakdown || plan.score_breakdown || null
    };
  };

  // 기본 샘플 데이터
  const defaultAnalysis = {
    summary: {
      currentPlan: '정보 없음',
      currentPrice: 0,
      requestedFeature: '요약 대기 중',
      customerProfile: '정보 없음',
      mainConcern: '정보 없음',
      opportunity: '정보 없음',
      consultationResult: '상담 대기 중'
    },
    recommendedPlans: []
  };

  // aiAnalysis 데이터 정규화
  const analysis = aiAnalysis ? {
    summary: normalizeSummary(aiAnalysis.summary) || defaultAnalysis.summary,
    recommendedPlans: (aiAnalysis.recommendedPlans || []).map(normalizePlan)
  } : defaultAnalysis;

  return (
    <PanelContainer>
      <PanelHeader>
        <Title>
          <FiZap style={{ color: '#f59e0b' }} />
          AI 요약 및 추천 요금제
        </Title>
      </PanelHeader>

      <SummarySection>
        <SectionTitle>
          <FiTrendingUp />
          AI 상담 요약
        </SectionTitle>
        <KeyPoint>
          <KeyPointLabel>현재 요금제:</KeyPointLabel>
          <KeyPointValue>{analysis.summary.currentPlan} (월 {analysis.summary.currentPrice.toLocaleString()}원)</KeyPointValue>
        </KeyPoint>
        <KeyPoint>
          <KeyPointLabel>고객 요구:</KeyPointLabel>
          <KeyPointValue>{analysis.summary.requestedFeature}</KeyPointValue>
        </KeyPoint>
        <KeyPoint>
          <KeyPointLabel>주요 관심:</KeyPointLabel>
          <KeyPointValue>{analysis.summary.mainConcern}</KeyPointValue>
        </KeyPoint>
        <KeyPoint>
          <KeyPointLabel>고객 특성:</KeyPointLabel>
          <KeyPointValue>{analysis.summary.customerProfile}</KeyPointValue>
        </KeyPoint>
        <KeyPoint>
          <KeyPointLabel>영업 기회:</KeyPointLabel>
          <KeyPointValue>{analysis.summary.opportunity}</KeyPointValue>
        </KeyPoint>
        <KeyPoint style={{ background: '#fef3c7', borderLeftColor: '#f59e0b' }}>
          <KeyPointLabel style={{ color: '#b45309' }}>상담 결과:</KeyPointLabel>
          <KeyPointValue style={{ fontWeight: '600' }}>{analysis.summary.consultationResult}</KeyPointValue>
        </KeyPoint>
      </SummarySection>

      <RecommendationSection>
        <SectionTitle>
          <FiPackage />
          AI 추천 요금제
        </SectionTitle>
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '12px', padding: '8px', background: '#f0f4ff', borderRadius: '8px' }}>
          💡 AI가 고객 상담 내용을 분석하여 3가지 유형의 요금제를 추천합니다.
        </div>

        {analysis.recommendedPlans.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
            상담 완료 후 AI 추천이 표시됩니다
          </div>
        ) : analysis.recommendedPlans.map((plan, index) => (
          <RecommendationCard
            key={plan.id}
            primary={plan.badge === 'best'}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <RecommendBadge type={plan.badge}>
              {plan.badge === 'best' && <><FiStar /> 최적</>}
              {plan.badge === 'upsell' && <><FiTrendingUp /> 업그레이드</>}
              {plan.badge === 'budget' && <><FiDollarSign /> 절약형</>}
            </RecommendBadge>

            <PlanName primary={plan.badge === 'best'}>
              {plan.name}
            </PlanName>

            <PlanPrice>
              <Price primary={plan.badge === 'best'}>
                {plan.discountedPrice.toLocaleString()}
              </Price>
              <PriceUnit primary={plan.badge === 'best'}>원/월</PriceUnit>
              {plan.discount && <Discount>{plan.discount}</Discount>}
            </PlanPrice>

            <PlanFeatures>
              {plan.features.map((feature, idx) => (
                <Feature key={idx} primary={plan.badge === 'best'}>
                  {idx === 0 && <FiWifi />}
                  {idx === 1 && <FiSmartphone />}
                  {idx === 2 && <FiUsers />}
                  {idx === 3 && <FiPackage />}
                  {feature}
                </Feature>
              ))}
            </PlanFeatures>

            {plan.comparison && (
              <ComparisonNote primary={plan.badge === 'best'}>
                💡 {plan.comparison}
              </ComparisonNote>
            )}

            {plan.score && (
              <ScoreBadge primary={plan.badge === 'best'}>
                AI 스코어: {plan.score.toFixed(1)}점
              </ScoreBadge>
            )}
          </RecommendationCard>
        ))}
      </RecommendationSection>
    </PanelContainer>
  );
};

export default AISummaryPanel;
