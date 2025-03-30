"""
통합검색_현장건의 과제 상세 내용 크롤링 클래스
"""
import concurrent.futures
import time
from typing import List
import pandas as pd
from tqdm import tqdm

from integ.models import ListItem, CombinedItem
from integ.detail.fetcher import DetailFetcher
from integ.detail.parser import DetailParser
from integ.detail.combiner import DetailCombiner
from integ.config import (DEFAULT_DELAY, DEFAULT_MAX_WORKERS)

class DetailCrawler:
    """현장건으 ㅣ과제 상세 내용 크롤러"""
    
    def __init__(self, delay_seconds: float = DEFAULT_DELAY, max_workers: int = DEFAULT_MAX_WORKERS):
        self.delay_seconds = delay_seconds
        self.max_workers = max_workers
        self.fetcher = DetailFetcher()
        self.parser = DetailParser()
        self.combiner = DetailCombiner()
    
    # 대외 래퍼
    def get_combined_dataframe(self, list_items: List[ListItem]) -> pd.DataFrame:
        """목록 아이템과 상세 내용을 결합한 데이터프레임 반환"""

        # 이 단계에서 list_items 중 "현장건의 과제"만 필터링한다
        print("전체 목록 중 현장건의 과제 항목만 필터링합니다.")
        print(f"전체 항목 수: {len(list_items)}")
        filtered_items = [item for item in list_items if item.pastreqType == "현장건의 과제"]
        print(f"필터링된 항목 수: {len(filtered_items)}")
        if not filtered_items:
            print("경고: '현장건의 과제' 항목이 없습니다.")
            return pd.DataFrame()

        ## 내부 메서드 호출
        combined_items = self._process_items(filtered_items)

        return pd.DataFrame([vars(item) for item in combined_items])
    
    def _process_items(self, list_items: List[ListItem]) -> List[CombinedItem]:
        """상세 페이지 크롤링 및 처리"""
        combined_items = []
        total_items = len(list_items)
        
        print(f"상세 내용 크롤링 시작: 총 {total_items}개 항목")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_single_item, item): item 
                      for item in list_items}
            
            with tqdm(total=total_items, desc="상세 크롤링") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    combined_item = future.result()
                    combined_items.append(combined_item)
                    pbar.update(1)
        
        self._print_summary()
        return combined_items
    
    def _process_single_item(self, list_item: ListItem) -> CombinedItem:
        """단일 항목 처리"""
        try:
            html = self.fetcher.get_html(list_item.dataIdx)
            detail_item = self.parser.parse(html, list_item.dataIdx)
            combined_item = self.combiner.combine(list_item, detail_item)
            time.sleep(self.delay_seconds)
            return combined_item
        except Exception as e:
            self.parser.stats.failed_items.append((list_item.dataIdx, str(e)))
            return self.combiner.combine(list_item, None)
            
    def _print_summary(self):
        """처리 결과 요약 출력"""
        stats = self.parser.stats
        if stats.regex_found_count > 0:
            print(f"참고: {stats.regex_found_count}개 항목은 정규식을 사용하여 '이유' 필드를 찾았습니다.")
        
        if stats.failed_items:
            print(f"경고: {len(stats.failed_items)}개 항목에서 문제가 발생했습니다.")
            for i, (idx, error) in enumerate(stats.failed_items[:3]):
                print(f"  - 실패 항목 #{i+1}: pastreqIdx={idx}, 오류={error[:100]}")
            if len(stats.failed_items) > 3:
                print(f"  - 그 외 {len(stats.failed_items)-3}개 항목...")

if __name__ == "__main__":
    import logging
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 테스트용 ListItem 생성
    test_item = ListItem(
        rownumber=3,
        dataIdx=1437752,
        pastreqType="현장건의 과제",
        title="한도제한 계좌 해제 편의성 확보",
        replyRegDate="2024-01-09",        
    )
    
    # try:
        # DetailCrawler 인스턴스 생성 (느린 크롤링을 위해 delay 증가)
    crawler = DetailCrawler(delay_seconds=1.0, max_workers=1)
    
    # 단일 항목 크롤링 테스트
    logger.info("단일 항목 크롤링 테스트 시작...")
    df = crawler.get_combined_dataframe([test_item])
    
    # 결과 출력
    logger.info("\n=== 크롤링 결과 ===")
    logger.info(f"데이터프레임 크기: {df.shape}")
    logger.info("\n=== 데이터프레임 내용 ===")
    
    # 결과 저장 (선택사항)
    import pandasgui as pg
    pg.show(df)