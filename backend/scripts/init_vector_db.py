#!/usr/bin/env python3
"""
벡터 DB 초기화 스크립트
CSV 요금제 데이터를 임베딩하여 ChromaDB에 저장
"""
import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_db_service import vector_db_service
from app.core.config import settings


def main():
    print("=" * 50)
    print("KT 요금제 벡터 DB 초기화")
    print("=" * 50)

    csv_path = os.path.abspath(settings.PLANS_CSV_PATH)
    print(f"\nCSV 경로: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"오류: CSV 파일을 찾을 수 없습니다: {csv_path}")
        sys.exit(1)

    print("\n요금제 데이터 로딩 및 임베딩 생성 중...")

    try:
        count = vector_db_service.load_plans_from_csv(csv_path)
        print(f"\n✓ {count}개의 요금제가 벡터 DB에 저장되었습니다.")

        # 테스트 검색
        print("\n테스트 검색: '데이터 무제한 요금제'")
        results = vector_db_service.search("데이터 무제한 요금제", top_k=3)

        print(f"\n검색 결과 ({len(results)}개):")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. {result['plan_name']}")
            print(f"     가격: {result['price']:,}원")
            print(f"     타겟: {result['target']}")
            print(f"     유사도: {result['similarity']:.3f}")

        print("\n" + "=" * 50)
        print("벡터 DB 초기화 완료!")
        print("=" * 50)

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
