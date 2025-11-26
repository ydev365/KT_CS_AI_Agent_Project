from firecrawl import FirecrawlApp
from openai import OpenAI
from typing import List, Dict, Optional
import json
from config import get_settings
from services.rag_service import RAGService

settings = get_settings()

# KT 요금제 URL 목록
KT_PLAN_URLS = [
    {"name": "요고 다이렉트", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1567&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 초이스", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1485&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 스페셜/베이직", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1283&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 심플", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1406&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 슬림", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1284&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 슬림(이월)", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1570&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G Y", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1358&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G Y틴", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1360&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 주니어", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1480&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 시니어", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1558&CateCode=6002&filter_code=81&option_code=109&pageSize=10"},
    {"name": "5G 웰컴", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1577&CateCode=6002&filter_code=81&option_code=109&pageSize=20"},
    {"name": "5G 복지", "url": "https://product.kt.com/wDic/productDetail.do?ItemCode=1438&CateCode=6002&filter_code=81&option_code=109&pageSize=20"},
]

EXTRACTION_PROMPT = """다음은 KT 요금제 웹페이지에서 크롤링한 내용입니다.
이 내용에서 요금제 정보를 추출하여 JSON 형식으로 반환해주세요.

추출할 정보:
- plan_name: 요금제명
- monthly_fee: 월정액 (여러 옵션이 있으면 범위로 표시, 예: "30,000원~69,000원")
- data_allowance: 데이터량 (예: "무제한", "30GB~110GB")
- call_allowance: 통화 제공량 (예: "기본 제공", "무제한")
- text_allowance: 문자 제공량 (예: "기본 제공", "무제한")
- target_age: 대상 연령/자격 조건 (예: "전체", "만 34세 이하", "만 65세 이상")
- benefits: 주요 혜택/특징 (콤마로 구분)
- additional_services: 부가서비스 (콤마로 구분)

JSON 형식으로만 응답해주세요. 다른 설명 없이 JSON만 출력하세요.
"""


class FirecrawlLoader:
    """Firecrawl을 이용한 KT 요금제 크롤링"""

    def __init__(self):
        self.firecrawl = FirecrawlApp(api_key=settings.firecrawl_api_key)
        self.openai = OpenAI(api_key=settings.openai_api_key)
        self.rag_service = RAGService()

    def crawl_url(self, url: str) -> Optional[str]:
        """단일 URL 크롤링"""
        try:
            result = self.firecrawl.scrape_url(
                url,
                params={"formats": ["markdown"]}
            )
            return result.get("markdown", "")
        except Exception as e:
            print(f"크롤링 오류 ({url}): {e}")
            return None

    def extract_plan_info(self, markdown_content: str, plan_name: str) -> Optional[Dict]:
        """GPT를 이용해 요금제 정보 추출"""
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": EXTRACTION_PROMPT},
                    {"role": "user", "content": f"요금제명: {plan_name}\n\n크롤링 내용:\n{markdown_content[:8000]}"}
                ],
                temperature=0,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            # JSON 파싱
            # JSON이 코드 블록으로 감싸진 경우 처리
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())

        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류 ({plan_name}): {e}")
            return None
        except Exception as e:
            print(f"정보 추출 오류 ({plan_name}): {e}")
            return None

    def load_single_plan(self, plan_info: Dict) -> bool:
        """단일 요금제 크롤링 및 저장"""
        print(f"크롤링 중: {plan_info['name']}...")

        # 크롤링
        content = self.crawl_url(plan_info['url'])
        if not content:
            print(f"  - 크롤링 실패")
            return False

        # 정보 추출
        extracted = self.extract_plan_info(content, plan_info['name'])
        if not extracted:
            print(f"  - 정보 추출 실패")
            return False

        # ChromaDB에 저장
        try:
            self.rag_service.add_plan(extracted)
            print(f"  - 저장 완료: {extracted.get('plan_name', plan_info['name'])}")
            return True
        except Exception as e:
            print(f"  - 저장 실패: {e}")
            return False

    def load_all_plans(self, skip_existing: bool = True) -> Dict:
        """모든 요금제 크롤링 및 저장

        Args:
            skip_existing: True면 이미 저장된 요금제는 건너뜀
        """
        results = {"success": [], "failed": [], "skipped": []}

        # 이미 저장된 요금제 이름 가져오기
        existing_names = set()
        if skip_existing:
            existing_names = self.rag_service.get_existing_plan_names()
            if existing_names:
                print(f"이미 저장된 요금제: {len(existing_names)}개")

        for plan_info in KT_PLAN_URLS:
            # 이미 저장된 요금제는 건너뛰기
            if skip_existing and plan_info['name'] in existing_names:
                print(f"건너뜀 (이미 존재): {plan_info['name']}")
                results["skipped"].append(plan_info['name'])
                continue

            if self.load_single_plan(plan_info):
                results["success"].append(plan_info['name'])
            else:
                results["failed"].append(plan_info['name'])

        print(f"\n=== 크롤링 완료 ===")
        print(f"건너뜀: {len(results['skipped'])}개")
        print(f"성공: {len(results['success'])}개")
        print(f"실패: {len(results['failed'])}개")

        return results

    def reload_all_plans(self) -> Dict:
        """모든 요금제 재크롤링 (기존 데이터 삭제 후)"""
        print("기존 데이터 삭제 중...")
        self.rag_service.clear_collection()
        return self.load_all_plans()


# CLI 실행용
if __name__ == "__main__":
    loader = FirecrawlLoader()
    loader.load_all_plans()
