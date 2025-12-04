#!/usr/bin/env python3
"""
벡터 DB 초기화 스크립트
CSV 요금제 및 부가서비스 데이터를 임베딩하여 ChromaDB에 저장
"""
import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_db_service import vector_db_service
from app.core.config import settings


def main():
    print("=" * 50)
    print("KT 요금제 & 부가서비스 벡터 DB 초기화")
    print("=" * 50)

    # 1. 요금제 데이터 로드
    plans_csv_path = os.path.abspath(settings.PLANS_CSV_PATH)
    print(f"\n[1] 요금제 CSV 경로: {plans_csv_path}")

    if not os.path.exists(plans_csv_path):
        print(f"오류: CSV 파일을 찾을 수 없습니다: {plans_csv_path}")
        sys.exit(1)

    print("\n요금제 데이터 로딩 및 임베딩 생성 중...")

    try:
        count = vector_db_service.load_plans_from_csv(plans_csv_path)
        print(f"✓ {count}개의 요금제가 벡터 DB에 저장되었습니다.")

        # 테스트 검색
        print("\n테스트 검색: '데이터 무제한 요금제'")
        results = vector_db_service.search("데이터 무제한 요금제", top_k=3)

        print(f"검색 결과 ({len(results)}개):")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['plan_name']} - {result['price']:,}원 (OTT: {result.get('has_ott', False)})")

    except Exception as e:
        print(f"\n요금제 로드 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 2. 부가서비스 데이터 로드
    addon_csv_path = os.path.abspath(settings.ADDON_SERVICES_CSV_PATH)
    print(f"\n[2] 부가서비스 CSV 경로: {addon_csv_path}")

    if not os.path.exists(addon_csv_path):
        print(f"경고: 부가서비스 CSV 파일을 찾을 수 없습니다: {addon_csv_path}")
        print("부가서비스 데이터 없이 진행합니다.")
    else:
        print("\n부가서비스 데이터 로딩 및 임베딩 생성 중...")

        try:
            addon_count = vector_db_service.load_addon_services_from_csv(addon_csv_path)
            print(f"✓ {addon_count}개의 부가서비스가 벡터 DB에 저장되었습니다.")

            # 테스트: OTT 부가서비스 최저가 조회
            print("\n테스트: OTT 부가서비스 최저가 TOP 5")
            cheapest = vector_db_service.get_cheapest_addon_by_ott()[:5]

            for i, addon in enumerate(cheapest, 1):
                print(f"  {i}. {addon['service_name']} - {addon['price']:,}원 ({addon['ott_type']})")

        except Exception as e:
            print(f"\n부가서비스 로드 오류: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 50)
    print("벡터 DB 초기화 완료!")
    print("=" * 50)


if __name__ == "__main__":
    main()
