"""
상세 내용 크롤링 래퍼 클래스
"""

import pandas as pd
from typing import List, Optional
import concurrent.futures
from tqdm import tqdm

from late.models import ListItem, DetailItem, CombinedItem
from late.detail.base_fetcher import BaseFetcher
from late.detail.base_parser import BaseParser
from late.detail.law.fetcher import LawFetcher
from late.detail.law.parser import LawParser
from late.detail.opinion.fetcher import OpinionFetcher
from late.detail.opinion.parser import OpinionParser
from late.detail.combiner import DetailCombiner
from common.ssl_adapter import get_legacy_session

class DetailCrawler:
    """금융위원회 회신사례 상세 내용 크롤러 (래퍼 클래스)"""
    
    def __init__(self, delay_seconds: float = 0.5, max_workers: int = 64):
        """
        Args:
            delay_seconds: 요청 간 지연 시간 (초)
            max_workers: 병렬 처리 시 최대 worker 수
        """
        self.delay_seconds = delay_seconds
        self.max_workers = max_workers
        self.combiner = DetailCombiner()
        
        # 통계 변수
        self.total_processed = 0
        self.failed_items = []
        
        # 문서 유형별 처리기 매핑
        self.fetcher_map = {
            "법령해석": LawFetcher,
            "비조치의견서": OpinionFetcher
        }
        
        self.parser_map = {
            "법령해석": LawParser,
            "비조치의견서": OpinionParser
        }

        # 세션 재사용을 위한 SSL Adapter 설정 (max_workers 만큼 풀 크기 지정)
        self.session = get_legacy_session(pool_maxsize=max_workers)
        
    def get_detail_item(self, idx: int, gubun: str) -> Optional[DetailItem]:
        """
        idx와 gubun 값으로 상세 내용을 가져와 파싱
        
        Args:
            idx: 문서 식별자
            gubun: 문서 유형 ('법령해석' 또는 '비조치의견서' 등)
            
        Returns:
            DetailItem 객체, 오류 발생 시 None
        """
        self.total_processed += 1
        try:
            # 적절한 Fetcher와 Parser 선택
            fetcher_class:BaseFetcher = self.fetcher_map.get(gubun)
            parser_class:BaseParser = self.parser_map.get(gubun)
            
            if not fetcher_class or not parser_class:
                self.failed_items.append((idx, gubun, f"지원하지 않는 문서 유형: {gubun}"))
                return None
                
            # 세션을 공유하여 인스턴스 생성
            fetcher:LawFetcher|OpinionFetcher = fetcher_class(delay_seconds=self.delay_seconds, session=self.session)
            parser:LawParser|OpinionParser = parser_class()
                
            # HTML 가져오기 : 페쳐 사용
            html_content = fetcher.fetch(idx)
            if not html_content:
                self.failed_items.append((idx, gubun, "HTML 요청 실패"))
                return None
                
            # HTML 파싱 : 파서 사용용
            detail_item = parser.parse(html_content, idx, gubun)
            return detail_item
        except Exception as e:
            # 실패 항목 기록
            self.failed_items.append((idx, gubun, str(e)))
            return None
    
    def _process_item(self, list_item: ListItem) -> CombinedItem:
        """단일 항목 처리를 위한 helper 함수 (병렬 처리용)"""
        detail_item = self.get_detail_item(list_item.idx, list_item.gubun)
        return self.combiner.combine(list_item, detail_item)
            
    def get_combined_dataframe(self, list_items: List[ListItem]) -> pd.DataFrame:
        """
        목록 아이템과 상세 내용을 결합한 데이터프레임 반환
        
        Args:
            list_items: 목록 아이템 리스트
            
        Returns:
            결합된 아이템의 DataFrame
        """
        total_items = len(list_items)
        combined_items = []
        
        # 통계 변수 초기화
        self.total_processed = 0
        self.failed_items = []
        
        print(f"상세 내용 크롤링 시작: 총 {total_items}개 항목")
        
        # 병렬 처리 구현
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_item, item): item for item in list_items}
            
            # tqdm을 사용한 진행 상황 표시
            with tqdm(total=total_items, desc="상세 크롤링") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    combined_item = future.result()
                    combined_items.append(combined_item)
                    pbar.update(1)
        
        # 크롤링 완료 후 요약 정보 출력
        print(f"상세 내용 크롤링 완료: 총 {len(combined_items)}개 항목")
        
        # 실패 항목 요약 출력
        if self.failed_items:
            print(f"경고: {len(self.failed_items)}개 항목에서 문제가 발생했습니다.")
            # 처음 3개만 상세 출력
            for i, (idx, gubun, error) in enumerate(self.failed_items[:3]):
                print(f"  - 실패 항목 #{i+1}: idx={idx}, gubun={gubun}, 오류={error[:100]}")
            if len(self.failed_items) > 3:
                print(f"  - 그 외 {len(self.failed_items)-3}개 항목...")
        
        return pd.DataFrame([vars(item) for item in combined_items])


if __name__ == "__main__":
    import logging
    import sys
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # try:
    # 테스트용 ListItem 생성 - 두 가지 유형 모두 포함
    test_items = [
        # 법령해석 샘플
        ListItem(
            rownumber=5,
            idx=5107,
            gubun="법령해석",
            category="",
            title="보장성 상품 청약 철회시 자료의 기록 및 유지관리 대상 범위 질의",
            regDate="2025.03.10",
            number="250077"

        ),
        # 비조치의견서 샘플
        ListItem(
            rownumber=6,
            idx=2256,
            gubun="비조치의견서",
            category="",
            title="방카슈랑스 판매비율 규제 관련 비조치의견서 요청",
            regDate="2025.03.12",
            number="250014"
        )
    ]
    
    logger.info(f"테스트 시작: 법령해석 1건(ID: {test_items[0].idx}), 비조치의견서 1건(ID: {test_items[1].idx})")
        
    # DetailCrawler 인스턴스 생성 (느린 크롤링을 위해 delay 증가)
    crawler = DetailCrawler(delay_seconds=1.0, max_workers=2)
    
    # 테스트 항목 크롤링
    logger.info("두 가지 유형 크롤링 테스트 시작...")
    df = crawler.get_combined_dataframe(test_items)
    
    # 결과 출력
    logger.info("\n=== 크롤링 결과 ===")
    logger.info(f"데이터프레임 크기: {df.shape}")
    
    # 결과 표시
    try:
        import pandasgui
        logger.info("PandasGUI로 결과 표시 중...")
        pandasgui.show(df)
    except ImportError:
        # PandasGUI가 없으면 콘솔에 출력
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 30)  # 컬럼 내용 일부만 표시
        logger.info(f"\n{df}")
        logger.info("전체 내용을 보려면 pip install pandasgui 후 실행하세요.")
            
    # except Exception as e:
    #     logger.error(f"테스트 중 오류 발생: {str(e)}", exc_info=True)
        