import React, { useState } from 'react';
import styled from 'styled-components';
import { FiSearch, FiTag, FiTrendingUp, FiChevronRight } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

const PanelContainer = styled.div`
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

const SearchContainer = styled.div`
  position: relative;
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #999;
  }
`;

const SearchIcon = styled(FiSearch)`
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
`;

const QuickTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
`;

const Tag = styled.button`
  background: ${props => props.active ? '#667eea' : '#f0f0f0'};
  color: ${props => props.active ? 'white' : '#666'};
  border: none;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    background: ${props => props.active ? '#5a6fdb' : '#e0e0e0'};
    transform: translateY(-1px);
  }
`;

const ResultsArea = styled.div`
  max-height: 400px;
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

const ResultCard = styled(motion.div)`
  background: #f9f9f9;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  
  &:hover {
    background: white;
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
`;

const ResultTitle = styled.h4`
  font-size: 0.95rem;
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ResultPrice = styled.div`
  font-size: 1.1rem;
  color: #667eea;
  font-weight: 700;
  margin-bottom: 8px;
`;

const ResultDescription = styled.p`
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
`;

const ResultTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
`;

const ResultTag = styled.span`
  background: ${props => {
    switch(props.type) {
      case 'discount': return '#10b981';
      case 'popular': return '#f59e0b';
      case 'new': return '#ef4444';
      default: return '#94a3b8';
    }
  }};
  color: white;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
`;

const RelevanceScore = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: #999;
  margin-top: 8px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #999;
  
  svg {
    font-size: 2.5rem;
    margin-bottom: 12px;
    opacity: 0.3;
  }
  
  p {
    font-size: 0.9rem;
  }
`;

const QuickSearchPanel = ({ onSearch, searchResults }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTag, setActiveTag] = useState(null);

  const quickSearchTags = [
    { id: 'all', label: '일반', icon: <FiTag /> },
    { id: 'youth', label: '청년(Y)', icon: <FiTrendingUp /> },
    { id: 'senior', label: '시니어', icon: <FiTag /> },
    { id: 'junior', label: '주니어', icon: <FiTag /> },
    { id: 'disabled', label: '장애인', icon: <FiTag /> },
    { id: 'foreigner', label: '외국인', icon: <FiTag /> },
    { id: 'addon', label: '부가서비스', icon: <FiTag /> },
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery);
    }
  };

  const handleTagClick = (tagId) => {
    setActiveTag(tagId);
    onSearch(tagId);
  };

  const handleResultClick = (result) => {
    // 결과 클릭 시 상세 정보 표시 또는 답변에 추가
    console.log('Selected result:', result);
  };

  return (
    <PanelContainer>
      <PanelHeader>
        <FiSearch />
        <Title>요금제 검색</Title>
      </PanelHeader>

      <SearchContainer>
        <SearchIcon />
        <form onSubmit={handleSearch}>
          <SearchInput
            type="text"
            placeholder="요금제 검색 (예: 청년, 5G, 가족결합)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      </SearchContainer>

      <QuickTags>
        {quickSearchTags.map(tag => (
          <Tag
            key={tag.id}
            active={activeTag === tag.id}
            onClick={() => handleTagClick(tag.id)}
          >
            {tag.icon}
            {tag.label}
          </Tag>
        ))}
      </QuickTags>

      <ResultsArea>
        {searchResults.length === 0 ? (
          <EmptyState>
            <FiSearch />
            <p>검색 결과가<br />여기에 표시됩니다</p>
          </EmptyState>
        ) : (
          <AnimatePresence>
            {searchResults.map((result, index) => (
              <ResultCard
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                onClick={() => handleResultClick(result)}
              >
                <ResultTitle>
                  {result.title}
                  <FiChevronRight />
                </ResultTitle>
                <ResultPrice>{result.price.toLocaleString()}원/월</ResultPrice>
                <ResultDescription>{result.description}</ResultDescription>
                <ResultTags>
                  {result.tags?.map((tag, idx) => (
                    <ResultTag key={idx} type={tag.type}>
                      {tag.label}
                    </ResultTag>
                  ))}
                </ResultTags>
                <RelevanceScore>
                  <FiTrendingUp />
                  관련도 {Math.round(result.relevance * 100)}%
                </RelevanceScore>
              </ResultCard>
            ))}
          </AnimatePresence>
        )}
      </ResultsArea>
    </PanelContainer>
  );
};

export default QuickSearchPanel;
