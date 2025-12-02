import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (추후 인증 토큰 추가 가능)
api.interceptors.request.use(
  (config) => {
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// 상담 관련 API
export const consultationApi = {
  // 상담 ID로 전체 정보 조회
  getConsultation: (consultationId) =>
    api.get(`/api/consultations/${consultationId}`),

  // 상담 ID로 대화 로그 조회
  getConversation: (consultationId) =>
    api.get(`/api/consultations/${consultationId}/conversation`),

  // 상담 ID로 AI 분석 결과 조회
  getAnalysis: (consultationId) =>
    api.get(`/api/consultations/${consultationId}/analysis`),

  // 고객 ID로 최신 상담 조회
  getLatestByCustomer: (customerId) =>
    api.get(`/api/consultations/customer/${customerId}/latest`),
};

// 고객 관련 API
export const customerApi = {
  // 고객 ID로 정보 조회
  getCustomer: (customerId) =>
    api.get(`/api/customers/${customerId}`),

  // 전화번호로 고객 정보 조회
  getCustomerByPhone: (phone) =>
    api.get(`/api/customers/phone/${phone}`),
};

// 요금제 관련 API
export const planApi = {
  // 요금제 검색
  searchPlans: ({ query, filters, page = 1, pageSize = 10 }) => {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (filters && filters.length > 0) params.append('filters', filters.join(','));
    params.append('page', page);
    params.append('pageSize', pageSize);

    return api.get(`/api/plans/search?${params.toString()}`);
  },
};

// 헬스 체크
export const healthCheck = () => api.get('/api/health');

export default api;
