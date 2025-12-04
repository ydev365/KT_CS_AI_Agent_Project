"""동적 가중치 기반 요금제 스코어링 서비스"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re


@dataclass
class CustomerNeeds:
    """고객 니즈 분석 결과"""
    data_priority: float = 0.2      # 데이터 중요도
    price_priority: float = 0.2     # 가격 중요도
    ott_priority: float = 0.2       # OTT 중요도
    roaming_priority: float = 0.1   # 해외로밍 중요도
    call_priority: float = 0.1      # 통화 중요도
    benefit_priority: float = 0.2   # 부가혜택 중요도

    # 고객이 원하는 구체적 조건
    desired_otts: List[str] = None      # 원하는 OTT 서비스
    min_data_gb: int = 0                # 최소 데이터량 (GB)
    max_price: int = 0                  # 최대 예산
    needs_roaming: bool = False         # 해외로밍 필요 여부
    needs_unlimited_call: bool = False  # 무제한 통화 필요 여부

    def __post_init__(self):
        if self.desired_otts is None:
            self.desired_otts = []


class ScoringService:
    """요금제 스코어링 서비스"""

    # 니즈 감지 키워드
    NEED_KEYWORDS = {
        'ott': {
            'keywords': ['넷플릭스', 'netflix', '티빙', 'tving', '디즈니', 'disney',
                        '유튜브', 'youtube', '웨이브', 'wavve', 'ott', '영상', '드라마', '영화',
                        '밀리', '밀리의서재', '지니', '뮤직', '음악'],
            'weight_boost': 0.35
        },
        'price': {
            'keywords': ['저렴', '싼', '싸게', '가격', '비용', '절약', '아끼', '예산',
                        '부담', '할인', '만원', '얼마'],
            'weight_boost': 0.35
        },
        'data': {
            'keywords': ['데이터', '기가', 'gb', '무제한', '용량', '많이', '부족',
                        '다써', '다 써', '초과', '속도'],
            'weight_boost': 0.30
        },
        'roaming': {
            'keywords': ['해외', '로밍', '여행', '출장', '외국', '비행기'],
            'weight_boost': 0.35
        },
        'call': {
            'keywords': ['통화', '전화', '음성', '분', '무제한 통화'],
            'weight_boost': 0.25
        }
    }

    # OTT 서비스 매핑
    OTT_SERVICES = {
        '넷플릭스': ['넷플릭스', 'netflix'],
        '티빙': ['티빙', 'tving'],
        '디즈니+': ['디즈니', 'disney', '디즈니플러스', 'disney+'],
        '유튜브프리미엄': ['유튜브', 'youtube', '유튜브프리미엄'],
        '웨이브': ['웨이브', 'wavve'],
        '밀리의서재': ['밀리', '밀리의서재', '밀리의 서재'],
        '지니뮤직': ['지니', '지니뮤직', '음악']
    }

    def analyze_customer_needs(self, conversation: List[Dict[str, Any]]) -> CustomerNeeds:
        """
        대화 내용에서 고객 니즈 분석 및 동적 가중치 설정

        Args:
            conversation: 대화 기록 리스트

        Returns:
            CustomerNeeds: 분석된 고객 니즈와 가중치
        """
        needs = CustomerNeeds()

        # 모든 고객 발화 추출
        customer_messages = []
        for msg in conversation:
            if msg.get('speaker') == 'customer':
                customer_messages.append(msg.get('content', '').lower())

        all_text = ' '.join(customer_messages)

        # 카테고리별 언급 횟수 계산
        category_counts = {}
        for category, config in self.NEED_KEYWORDS.items():
            count = sum(1 for kw in config['keywords'] if kw in all_text)
            category_counts[category] = count

        total_mentions = sum(category_counts.values())

        # 동적 가중치 설정
        if total_mentions > 0:
            # 기본 가중치
            base_weight = 0.15

            # 언급된 카테고리에 가중치 부여
            for category, count in category_counts.items():
                if count > 0:
                    boost = self.NEED_KEYWORDS[category]['weight_boost']
                    # 언급 횟수에 비례하여 가중치 증가 (최대 boost까지)
                    weight = base_weight + min(boost, boost * (count / max(total_mentions, 1)))

                    if category == 'ott':
                        needs.ott_priority = weight
                    elif category == 'price':
                        needs.price_priority = weight
                    elif category == 'data':
                        needs.data_priority = weight
                    elif category == 'roaming':
                        needs.roaming_priority = weight
                    elif category == 'call':
                        needs.call_priority = weight

        # 가중치 정규화 (합이 1이 되도록)
        total_weight = (needs.data_priority + needs.price_priority +
                       needs.ott_priority + needs.roaming_priority +
                       needs.call_priority + needs.benefit_priority)

        if total_weight > 0:
            needs.data_priority /= total_weight
            needs.price_priority /= total_weight
            needs.ott_priority /= total_weight
            needs.roaming_priority /= total_weight
            needs.call_priority /= total_weight
            needs.benefit_priority /= total_weight

        # 구체적 조건 추출
        needs.desired_otts = self._extract_desired_otts(all_text)
        needs.min_data_gb = self._extract_data_requirement(all_text)
        needs.max_price = self._extract_price_budget(all_text)
        needs.needs_roaming = any(kw in all_text for kw in self.NEED_KEYWORDS['roaming']['keywords'])
        needs.needs_unlimited_call = '무제한' in all_text and any(kw in all_text for kw in ['통화', '전화'])

        return needs

    def _extract_desired_otts(self, text: str) -> List[str]:
        """원하는 OTT 서비스 추출"""
        desired = []
        for ott_name, keywords in self.OTT_SERVICES.items():
            if any(kw in text for kw in keywords):
                desired.append(ott_name)
        return desired

    def _extract_data_requirement(self, text: str) -> int:
        """데이터 요구량 추출 (GB)"""
        # "100기가", "50GB" 등 패턴 매칭
        patterns = [
            r'(\d+)\s*(?:기가|gb|GB)',
            r'(\d+)\s*(?:G|g)(?:\s|$)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        # 무제한 요청
        if '무제한' in text and '데이터' in text:
            return 999  # 무제한 표시

        return 0

    def _extract_price_budget(self, text: str) -> int:
        """예산 추출 (원)"""
        # "5만원", "50000원" 등 패턴 매칭
        patterns = [
            r'(\d+)\s*만\s*원',
            r'(\d{4,6})\s*원'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                if '만' in pattern:
                    return value * 10000
                return value

        return 0

    def calculate_plan_score(
        self,
        plan: Dict[str, Any],
        needs: CustomerNeeds,
        all_plans: List[Dict[str, Any]]
    ) -> float:
        """
        요금제 점수 계산

        Args:
            plan: 요금제 정보
            needs: 고객 니즈
            all_plans: 전체 요금제 리스트 (정규화용)

        Returns:
            float: 0~100 점수
        """
        scores = {}

        # 1. 데이터 점수
        scores['data'] = self._score_data(plan, needs, all_plans)

        # 2. 가격 점수
        scores['price'] = self._score_price(plan, needs, all_plans)

        # 3. OTT 점수
        scores['ott'] = self._score_ott(plan, needs)

        # 4. 해외로밍 점수
        scores['roaming'] = self._score_roaming(plan, needs)

        # 5. 통화 점수
        scores['call'] = self._score_call(plan, needs)

        # 6. 부가혜택 점수
        scores['benefit'] = self._score_benefits(plan)

        # 가중치 적용 총점 계산
        total_score = (
            scores['data'] * needs.data_priority +
            scores['price'] * needs.price_priority +
            scores['ott'] * needs.ott_priority +
            scores['roaming'] * needs.roaming_priority +
            scores['call'] * needs.call_priority +
            scores['benefit'] * needs.benefit_priority
        )

        # 최소 점수 보정 (기본 점수 + 가중치 점수)
        # 기본 매칭도 50점 + 추가 점수 최대 50점
        adjusted_score = 50 + (total_score / 2)

        return round(min(100, adjusted_score), 1)

    def _score_data(self, plan: Dict, needs: CustomerNeeds, all_plans: List[Dict]) -> float:
        """데이터 점수 (0~100)"""
        data_str = str(plan.get('data_gb', '0')).lower()

        # 무제한이면 만점
        if '무제한' in data_str:
            return 100

        # 숫자 추출
        match = re.search(r'(\d+)', data_str)
        if not match:
            return 0

        data_gb = int(match.group(1))

        # 고객 요구량 충족 여부
        if needs.min_data_gb > 0:
            if data_gb >= needs.min_data_gb:
                return min(100, 70 + (data_gb - needs.min_data_gb) * 2)
            else:
                return max(0, 50 * (data_gb / needs.min_data_gb))

        # 요구량 없으면 상대 평가
        all_data = []
        for p in all_plans:
            d = str(p.get('data_gb', '0'))
            if '무제한' in d:
                all_data.append(500)
            else:
                m = re.search(r'(\d+)', d)
                if m:
                    all_data.append(int(m.group(1)))

        if all_data:
            max_data = max(all_data)
            return (data_gb / max_data) * 100 if max_data > 0 else 50

        return 50

    def _score_price(self, plan: Dict, needs: CustomerNeeds, all_plans: List[Dict]) -> float:
        """가격 점수 (0~100) - 낮을수록 높은 점수"""
        price = plan.get('price', 0)
        if not price:
            return 50

        # 예산 내 여부
        if needs.max_price > 0:
            if price <= needs.max_price:
                # 예산 내: 저렴할수록 높은 점수
                return 70 + (1 - price / needs.max_price) * 30
            else:
                # 예산 초과: 초과율에 따라 감점
                over_ratio = (price - needs.max_price) / needs.max_price
                return max(0, 50 - over_ratio * 50)

        # 예산 없으면 상대 평가 (저렴할수록 높은 점수)
        all_prices = [p.get('price', 0) for p in all_plans if p.get('price')]
        if all_prices:
            min_price = min(all_prices)
            max_price = max(all_prices)
            if max_price > min_price:
                return 100 - ((price - min_price) / (max_price - min_price)) * 100

        return 50

    def _score_ott(self, plan: Dict, needs: CustomerNeeds) -> float:
        """OTT 점수 (0~100)"""
        choice = str(plan.get('choice', '') or '').lower()
        plus = str(plan.get('plus', '') or '').lower()
        all_benefits = choice + ' ' + plus

        # OTT 없으면 0점
        if not choice or choice == '없음':
            if not plus or plus == '없음':
                return 0

        # 원하는 OTT가 있는 경우
        if needs.desired_otts:
            matched = 0
            for ott in needs.desired_otts:
                ott_keywords = self.OTT_SERVICES.get(ott, [ott.lower()])
                if any(kw in all_benefits for kw in ott_keywords):
                    matched += 1

            if matched == len(needs.desired_otts):
                return 100  # 모두 매칭
            elif matched > 0:
                return 50 + (matched / len(needs.desired_otts)) * 50  # 부분 매칭
            else:
                return 20  # OTT는 있지만 원하는 건 없음

        # 특정 OTT 요청 없으면 OTT 유무만 평가
        ott_count = sum(1 for ott_list in self.OTT_SERVICES.values()
                       for kw in ott_list if kw in all_benefits)
        return min(100, 30 + ott_count * 15)

    def _score_roaming(self, plan: Dict, needs: CustomerNeeds) -> float:
        """해외로밍 점수 (0~100)"""
        roaming = str(plan.get('data_roam', '') or '').lower()

        if not roaming or roaming == 'none':
            return 0 if needs.needs_roaming else 50

        # 무제한 로밍
        if '무제한' in roaming:
            return 100

        # 숫자 추출 (GB)
        match = re.search(r'(\d+)', roaming)
        if match:
            gb = int(match.group(1))
            if needs.needs_roaming:
                return min(100, 50 + gb * 10)
            return min(100, 30 + gb * 10)

        return 50

    def _score_call(self, plan: Dict, needs: CustomerNeeds) -> float:
        """통화 점수 (0~100)"""
        call = str(plan.get('call', '') or '').lower()

        if '무제한' in call:
            return 100

        # 분 단위 추출
        match = re.search(r'(\d+)', call)
        if match:
            minutes = int(match.group(1))
            if needs.needs_unlimited_call:
                return min(80, minutes / 5)  # 무제한 원하는데 제한이면 최대 80점
            return min(100, 50 + minutes / 10)

        return 50

    def _score_benefits(self, plan: Dict) -> float:
        """부가혜택 점수 (0~100)"""
        score = 0

        # 멤버십 등급
        membership = str(plan.get('membership', '') or '').upper()
        if 'VVIP' in membership:
            score += 30
        elif 'VIP' in membership:
            score += 20
        elif membership:
            score += 10

        # 보험 혜택
        if plan.get('insurance'):
            score += 20

        # 스마트기기 혜택
        if plan.get('smart_device'):
            score += 15

        # 데이터 쉐어
        if plan.get('data_share'):
            score += 15

        # Y혜택 (34세 이하)
        if plan.get('y_dom'):
            score += 10

        # 기타 혜택
        if plan.get('benefits1'):
            score += 5
        if plan.get('benefits2'):
            score += 5

        return min(100, score)

    def select_recommendations(
        self,
        plans: List[Dict[str, Any]],
        needs: CustomerNeeds
    ) -> Tuple[Dict, Dict, Dict]:
        """
        스코어링 기반 3가지 유형 요금제 선정

        Args:
            plans: 후보 요금제 리스트
            needs: 고객 니즈

        Returns:
            Tuple[최적형, 업그레이드형, 절약형]
        """
        if not plans:
            return None, None, None

        # 모든 요금제 점수 계산
        scored_plans = []
        for plan in plans:
            score = self.calculate_plan_score(plan, needs, plans)
            scored_plans.append({
                'plan': plan,
                'score': score,
                'price': plan.get('price', 0)
            })

        # 점수순 정렬
        scored_plans.sort(key=lambda x: x['score'], reverse=True)

        # 가격 기준 분류
        prices = [sp['price'] for sp in scored_plans if sp['price'] > 0]
        if prices:
            avg_price = sum(prices) / len(prices)
        else:
            avg_price = 70000

        # 최적형: 총점 1위
        best = scored_plans[0]['plan'] if scored_plans else None
        best_price = scored_plans[0]['price'] if scored_plans else 0

        # 업그레이드형: 최적형보다 가격이 높은 요금제 중 점수 높은 것
        upsell = None
        for sp in scored_plans:
            if sp['price'] > best_price and sp['plan'] != best:
                upsell = sp['plan']
                break

        # 업그레이드형이 없으면 전체 중 가장 비싼 것 (최적형 제외)
        if not upsell:
            price_sorted_desc = sorted(scored_plans, key=lambda x: x['price'], reverse=True)
            for sp in price_sorted_desc:
                if sp['plan'] != best:
                    upsell = sp['plan']
                    break

        # 절약형: 최적형보다 가격이 낮은 요금제 중 점수 높은 것
        budget = None
        for sp in scored_plans:
            if sp['price'] < best_price and sp['plan'] != best and sp['plan'] != upsell:
                budget = sp['plan']
                break

        # 절약형이 없으면 가장 저렴한 것 (최적형/업그레이드형 제외)
        if not budget:
            price_sorted_asc = sorted(scored_plans, key=lambda x: x['price'])
            for sp in price_sorted_asc:
                if sp['plan'] != best and sp['plan'] != upsell:
                    budget = sp['plan']
                    break

        # 디버깅 로그
        print(f"[RECOMMEND] Best: {best.get('plan_name') if best else None} ({best_price}원)")
        print(f"[RECOMMEND] Upsell: {upsell.get('plan_name') if upsell else None}")
        print(f"[RECOMMEND] Budget: {budget.get('plan_name') if budget else None}")

        return best, upsell, budget

    def get_score_breakdown(
        self,
        plan: Dict[str, Any],
        needs: CustomerNeeds,
        all_plans: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """점수 상세 내역 반환 (디버깅/설명용)"""
        return {
            'data_score': self._score_data(plan, needs, all_plans),
            'price_score': self._score_price(plan, needs, all_plans),
            'ott_score': self._score_ott(plan, needs),
            'roaming_score': self._score_roaming(plan, needs),
            'call_score': self._score_call(plan, needs),
            'benefit_score': self._score_benefits(plan),
            'weights': {
                'data': needs.data_priority,
                'price': needs.price_priority,
                'ott': needs.ott_priority,
                'roaming': needs.roaming_priority,
                'call': needs.call_priority,
                'benefit': needs.benefit_priority
            }
        }


# 싱글톤 인스턴스
scoring_service = ScoringService()
