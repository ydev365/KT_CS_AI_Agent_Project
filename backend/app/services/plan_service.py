import csv
import os
from typing import List, Optional
from ..schemas.plan import PlanSearchResult, PlanSearchResponse, PlanTag


# CSV 파일 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANS_CSV_PATH = os.path.join(BASE_DIR, "data", "plans.csv")
ADDON_CSV_PATH = os.path.join(BASE_DIR, "data", "addon_services.csv")


# 퀵 태그 → target 필터 매핑 (리스트면 OR 조건)
TAG_TO_TARGET = {
    'all': None,  # 전체 요금제 표시 (필터 없음)
    'youth': ['만 34세 이하'],
    'teen': ['만 18세 이하'],
    'senior': ['만 65세 이상', '만 75세 이상', '만 80세 이상'],  # 시니어 전체
    'junior': ['만 12세 이하'],
    'disabled': ['장애인'],
    'foreigner': ['외국인'],
    'addon': 'addon',  # 부가서비스는 별도 처리
}


def load_plans_from_csv() -> List[dict]:
    """plans.csv에서 요금제 로드"""
    plans = []
    try:
        with open(PLANS_CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                plans.append(row)
    except Exception as e:
        print(f"[PLAN SERVICE] Error loading plans.csv: {e}")
    return plans


def load_addons_from_csv() -> List[dict]:
    """addon_services.csv에서 부가서비스 로드"""
    addons = []
    try:
        with open(ADDON_CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addons.append(row)
    except Exception as e:
        print(f"[PLAN SERVICE] Error loading addon_services.csv: {e}")
    return addons


def has_ott(plan: dict) -> bool:
    """OTT 포함 여부 확인"""
    choice = plan.get('choice(1)', '') or plan.get('choice', '')
    if not choice or choice == '없음':
        return False
    # OTT 관련 키워드 확인
    ott_keywords = ['티빙', '넷플릭스', '유튜브', '디즈니', '지니', '밀리', '웨이브']
    return any(keyword in choice for keyword in ott_keywords)


def get_ott_list(plan: dict) -> str:
    """OTT 목록 반환"""
    choice = plan.get('choice(1)', '') or plan.get('choice', '')
    if not choice or choice == '없음':
        return ''
    return choice


def search_plans(
    query: Optional[str] = None,
    filters: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 100
) -> PlanSearchResponse:
    """요금제 검색 (CSV 기반 간단 검색)"""
    print(f"[PLAN SEARCH] query={query}, filters={filters}")

    # 부가서비스 검색인지 확인
    is_addon_search = filters and 'addon' in filters

    if is_addon_search:
        return search_addons(query, page, page_size)

    # 요금제 로드
    all_plans = load_plans_from_csv()
    results = []

    # 필터 적용 (target 기준)
    target_filter = None
    if filters:
        for f in filters:
            if f in TAG_TO_TARGET:
                target_filter = TAG_TO_TARGET[f]
                break

    for plan in all_plans:
        # target 필터 적용 (None이면 전체 표시)
        if target_filter is not None:
            plan_target = plan.get('target', '전체')
            # 리스트면 OR 조건으로 매칭
            if isinstance(target_filter, list):
                if not any(t in plan_target for t in target_filter):
                    continue
            else:
                if target_filter not in plan_target:
                    continue

        # 검색어 필터 (제목에서 검색)
        plan_name = plan.get('plan_name', '')
        if query and query.lower() not in plan_name.lower():
            # 검색어가 데이터나 가격에도 없으면 제외
            data_gb = plan.get('data_gb', '')
            if query.lower() not in data_gb.lower():
                continue

        results.append(plan)

    # 결과 변환
    search_results = []
    for i, plan in enumerate(results):
        plan_name = plan.get('plan_name', '알 수 없음')
        price = int(plan.get('price', 0) or 0)
        data_gb = plan.get('data_gb', '정보 없음')
        ott_included = has_ott(plan)
        ott_list = get_ott_list(plan)

        # 태그 생성
        tags = []
        if ott_included:
            tags.append(PlanTag(type='popular', label='OTT 포함'))
        if '무제한' in data_gb:
            tags.append(PlanTag(type='discount', label='무제한'))

        target = plan.get('target', '전체')
        if target != '전체':
            tags.append(PlanTag(type='new', label=target))

        # 설명: 데이터 + OTT 정보
        description = f"데이터: {data_gb}"
        if ott_list:
            # OTT 목록이 너무 길면 줄임
            if len(ott_list) > 30:
                description += f" | OTT: {ott_list[:30]}..."
            else:
                description += f" | OTT: {ott_list}"

        search_results.append(PlanSearchResult(
            id=str(i + 1),
            title=plan_name,
            price=price,
            description=description,
            tags=tags,
            relevance=max(0.5, 0.99 - (i * 0.02))
        ))

    # 페이지네이션
    total_count = len(search_results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_results = search_results[start_idx:end_idx]

    print(f"[PLAN SEARCH] found {total_count} plans, returning {len(paginated_results)}")

    return PlanSearchResponse(
        results=paginated_results,
        totalCount=total_count,
        pageNumber=page,
        pageSize=page_size
    )


def parse_addon_price(price_str: str) -> int:
    """부가서비스 가격 파싱 (프로모션가 우선)"""
    if not price_str:
        return 0
    # "판매가 13,000원 프로모션가 9,900원" -> 9900
    # "4,000원" -> 4000
    import re
    # 프로모션가가 있으면 프로모션가 사용
    promo_match = re.search(r'프로모션가\s*([\d,]+)원', price_str)
    if promo_match:
        return int(promo_match.group(1).replace(',', ''))
    # 없으면 첫 번째 숫자 사용
    price_match = re.search(r'([\d,]+)원', price_str)
    if price_match:
        return int(price_match.group(1).replace(',', ''))
    return 0


def search_addons(
    query: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
) -> PlanSearchResponse:
    """부가서비스 검색"""
    all_addons = load_addons_from_csv()
    results = []

    # CSV 컬럼명 확인 (첫 번째 행의 키 이름들)
    price_key = None
    if all_addons:
        keys = list(all_addons[0].keys())
        # 월정액 관련 컬럼 찾기
        for key in keys:
            if '월정액' in key:
                price_key = key
                break

    for addon in all_addons:
        # 첫 번째 컬럼 (요금제 이름)
        addon_name = addon.get('요금제', '')

        # 검색어 필터
        if query and query.lower() not in addon_name.lower():
            continue

        results.append(addon)

    # 결과 변환
    search_results = []
    for i, addon in enumerate(results):
        addon_name = addon.get('요금제', '알 수 없음')
        price_str = addon.get(price_key, '0') if price_key else '0'
        price = parse_addon_price(price_str)

        # 설명 생성
        video_quality = addon.get('영상 화질', '')
        streams = addon.get('동시 스트리밍 가능 기기 수', '')
        benefits = addon.get('혜택', '')

        description_parts = []
        if video_quality:
            description_parts.append(f"화질: {video_quality}")
        if streams:
            description_parts.append(f"동시접속: {streams}대")

        description = ' | '.join(description_parts) if description_parts else (benefits[:50] if benefits else '부가서비스')

        # 태그 생성 (OTT 종류 감지)
        tags = []
        if '넷플릭스' in addon_name:
            tags.append(PlanTag(type='popular', label='넷플릭스'))
        elif '디즈니' in addon_name:
            tags.append(PlanTag(type='popular', label='디즈니+'))
        elif '유튜브' in addon_name:
            tags.append(PlanTag(type='popular', label='유튜브'))
        elif '티빙' in addon_name:
            tags.append(PlanTag(type='popular', label='티빙'))
        elif '밀리' in addon_name:
            tags.append(PlanTag(type='new', label='전자책'))
        elif '지니' in addon_name:
            tags.append(PlanTag(type='new', label='음악'))
        elif '매거진' in addon_name:
            tags.append(PlanTag(type='new', label='매거진'))

        search_results.append(PlanSearchResult(
            id=f"addon_{i + 1}",
            title=addon_name,
            price=price,
            description=description,
            tags=tags,
            relevance=max(0.5, 0.99 - (i * 0.02))
        ))

    # 페이지네이션
    total_count = len(search_results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_results = search_results[start_idx:end_idx]

    print(f"[ADDON SEARCH] found {total_count} addons, returning {len(paginated_results)}")

    return PlanSearchResponse(
        results=paginated_results,
        totalCount=total_count,
        pageNumber=page,
        pageSize=page_size
    )
