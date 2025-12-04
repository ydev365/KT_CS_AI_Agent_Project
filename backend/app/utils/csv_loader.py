import pandas as pd
from typing import List, Dict, Any, Optional
import os


def load_plans_csv(csv_path: str) -> List[Dict[str, Any]]:
    """CSV 파일에서 요금제 데이터 로드"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    # NaN 값을 None으로 변환
    df = df.where(pd.notnull(df), None)

    plans = []
    for _, row in df.iterrows():
        plan = {
            "plan_name": row.get("plan_name"),
            "price": int(row.get("price", 0)) if row.get("price") else 0,
            "data_gb": row.get("data_gb"),
            "data_roam": row.get("data_roam"),
            "call": row.get("call"),
            "message": row.get("message"),
            "hotspot": row.get("hotspot"),
            "choice": row.get("choice(1)"),
            "plus": row.get("plus(1)"),
            "membership": row.get("membership"),
            "insurance": row.get("insurance"),
            "smart_device": row.get("smart_device"),
            "data_share": row.get("data_share"),
            "y_dom": row.get("y_dom(under35)"),
            "target": row.get("target", "전체"),
            "benefits1": row.get("benefits1"),
            "benefits2": row.get("benefits2")
        }
        plans.append(plan)

    return plans


def plan_to_document(plan: Dict[str, Any]) -> str:
    """요금제 정보를 검색 가능한 문서로 변환"""
    doc_parts = [
        f"요금제명: {plan['plan_name']}",
        f"월정액: {plan['price']:,}원" if plan['price'] else "",
        f"데이터: {plan['data_gb']}" if plan['data_gb'] else "",
        f"해외로밍: {plan['data_roam']}" if plan['data_roam'] else "",
        f"통화: {plan['call']}" if plan['call'] else "",
        f"문자: {plan['message']}" if plan['message'] else "",
        f"테더링: {plan['hotspot']}" if plan['hotspot'] else "",
        f"멤버십: {plan['membership']}" if plan['membership'] else "",
        f"대상: {plan['target']}" if plan['target'] else "",
    ]

    # 선택 혜택 (OTT 서비스 포함) - 있을 때만 표시
    if plan.get('choice'):
        choice_str = plan['choice']
        doc_parts.append(f"[선택혜택] {choice_str}")
        # OTT 서비스 키워드 강조
        if '넷플릭스' in choice_str:
            doc_parts.append("→ 넷플릭스 선택 가능")
        if '티빙' in choice_str:
            doc_parts.append("→ 티빙 선택 가능")
        if '디즈니' in choice_str:
            doc_parts.append("→ 디즈니플러스 선택 가능")
        if '유튜브' in choice_str:
            doc_parts.append("→ 유튜브프리미엄 선택 가능")
    else:
        doc_parts.append("[선택혜택] 없음")

    # 플러스 혜택 - 있을 때만 표시
    if plan.get('plus'):
        doc_parts.append(f"[플러스혜택] {plan['plus']}")
    else:
        doc_parts.append("[플러스혜택] 없음")

    # 추가 혜택
    if plan.get('insurance'):
        doc_parts.append(f"보험혜택: {plan['insurance']}")
    if plan.get('smart_device'):
        doc_parts.append(f"스마트기기: {plan['smart_device']}")
    if plan.get('data_share'):
        doc_parts.append(f"데이터쉐어링: {plan['data_share']}")
    if plan.get('y_dom'):
        doc_parts.append(f"Y혜택(34세이하): {plan['y_dom']}")

    # 부가 혜택
    if plan.get('benefits1'):
        doc_parts.append(f"[부가혜택1] {plan['benefits1']}")
    if plan.get('benefits2'):
        doc_parts.append(f"[부가혜택2] {plan['benefits2']}")

    return "\n".join([p for p in doc_parts if p])


def get_plan_metadata(plan: Dict[str, Any]) -> Dict[str, Any]:
    """요금제의 메타데이터 추출 (필터링용)"""
    # OTT 포함 여부: choice 컬럼에 값이 있으면 OTT 선택 가능
    has_ott = bool(plan.get("choice"))

    return {
        "plan_name": plan["plan_name"],
        "price": plan["price"],
        "target": plan["target"] or "전체",
        "has_unlimited_data": "무제한" in str(plan.get("data_gb", "")),
        "membership": plan.get("membership") or "",
        "has_ott": has_ott
    }


def parse_price(price_str: str) -> int:
    """가격 문자열에서 숫자 추출 (프로모션가 우선)"""
    if not price_str or pd.isna(price_str):
        return 0

    price_str = str(price_str)

    # 프로모션가가 있으면 프로모션가 사용
    if "프로모션가" in price_str:
        import re
        match = re.search(r'프로모션가\s*([\d,]+)원', price_str)
        if match:
            return int(match.group(1).replace(',', ''))

    # 판매가만 있는 경우
    if "판매가" in price_str:
        import re
        match = re.search(r'판매가\s*([\d,]+)원', price_str)
        if match:
            return int(match.group(1).replace(',', ''))

    # 그냥 숫자만 있는 경우 (예: "9,900원" 또는 "9900")
    import re
    match = re.search(r'([\d,]+)', price_str)
    if match:
        return int(match.group(1).replace(',', ''))

    return 0


def load_addon_services_csv(csv_path: str) -> List[Dict[str, Any]]:
    """부가서비스 CSV 파일 로드"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    df = df.where(pd.notnull(df), None)

    services = []
    for _, row in df.iterrows():
        # 가격 컬럼명 찾기
        price_col = None
        for col in df.columns:
            if '월정액' in col or '가격' in col:
                price_col = col
                break

        price = parse_price(row.get(price_col)) if price_col else 0
        service_name = row.get("요금제") or row.get("서비스명") or ""

        # OTT 종류 판별
        ott_type = None
        service_name_lower = str(service_name).lower()
        if "넷플릭스" in service_name_lower or "netflix" in service_name_lower:
            ott_type = "넷플릭스"
        elif "티빙" in service_name_lower or "tving" in service_name_lower:
            ott_type = "티빙"
        elif "디즈니" in service_name_lower or "disney" in service_name_lower:
            ott_type = "디즈니+"
        elif "유튜브" in service_name_lower or "youtube" in service_name_lower:
            ott_type = "유튜브프리미엄"
        elif "지니" in service_name_lower:
            ott_type = "지니뮤직"
        elif "밀리" in service_name_lower:
            ott_type = "밀리의서재"
        elif "매거진" in service_name_lower:
            ott_type = "매거진"

        service = {
            "service_name": service_name,
            "price": price,
            "ott_type": ott_type,
            "video_quality": row.get("영상 화질"),
            "audio_quality": row.get("오디오 품질"),
            "simultaneous_streams": row.get("동시 스트리밍 가능 기기 수"),
            "coffee_benefit": row.get("메가MGC커피(매월 가입일자에 문자메시지로 발송)"),
            "starbucks_benefit": row.get("스타벅스"),
            "extra_benefit": row.get("혜택"),
            "youtube_premium": row.get("유튜브 프리미엄"),
            "lotte_cinema": row.get("롯데시네마")
        }
        services.append(service)

    return services


def addon_service_to_document(service: Dict[str, Any]) -> str:
    """부가서비스 정보를 검색 가능한 문서로 변환"""
    doc_parts = [
        f"[OTT 부가서비스]",
        f"서비스명: {service['service_name']}",
        f"월정액: {service['price']:,}원" if service['price'] else "",
        f"OTT 종류: {service['ott_type']}" if service['ott_type'] else "",
    ]

    if service.get('video_quality'):
        doc_parts.append(f"영상 화질: {service['video_quality']}")
    if service.get('audio_quality'):
        doc_parts.append(f"오디오 품질: {service['audio_quality']}")
    if service.get('simultaneous_streams'):
        doc_parts.append(f"동시 스트리밍: {service['simultaneous_streams']}대")
    if service.get('coffee_benefit'):
        doc_parts.append(f"커피 혜택: {service['coffee_benefit']}")
    if service.get('starbucks_benefit'):
        doc_parts.append(f"스타벅스 혜택: {service['starbucks_benefit']}")
    if service.get('extra_benefit'):
        doc_parts.append(f"추가 혜택: {service['extra_benefit']}")

    return "\n".join([p for p in doc_parts if p])


def get_addon_service_metadata(service: Dict[str, Any]) -> Dict[str, Any]:
    """부가서비스 메타데이터 추출"""
    return {
        "service_name": service["service_name"],
        "price": service["price"],
        "ott_type": service["ott_type"] or "",
        "is_addon_service": True  # 부가서비스 구분용
    }
