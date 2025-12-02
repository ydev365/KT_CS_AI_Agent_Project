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
    return {
        "plan_name": plan["plan_name"],
        "price": plan["price"],
        "target": plan["target"] or "전체",
        "has_unlimited_data": "무제한" in str(plan.get("data_gb", "")),
        "membership": plan.get("membership") or ""
    }
