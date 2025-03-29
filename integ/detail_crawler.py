"""
통합회신사례 상세 페이지 크롤러
"""
import logging
import concurrent.futures
from typing import List

from bs4 import BeautifulSoup

from .config import DETAIL_URL
from .models import ListItem, DetailItem
from .utils import delay
from .detail.factory import DetailCrawlerFactory

logger = logging.getLogger(__name__)

class DetailCrawler:
    """상세 페이지 크롤러"""
    
    def __init__(self, delay_seconds: float = 0.5, max_workers: int = 10):
        """
        Args:
            delay_seconds: 요청 간 지연 시간
            max_workers: 병렬 처리 시 최대 worker 수
        """
        self.delay_seconds = delay_seconds
        self.max_workers = max_workers
        self.factory = DetailCrawlerFactory()
    
    def crawl(self, list_items: List[ListItem]) -> List[DetailItem]:
        """상세 페이지 크롤링 실행"""
        logger.info(f"상세 페이지 크롤링 시작: {len(list_items)}개 항목")
        
        detail_items = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(self._fetch_detail, item): item 
                for item in list_items
            }
            
            for future in concurrent.futures.as_completed(future_to_item):
                list_item = future_to_item[future]
                try:
                    detail_item = future.result()
                    if detail_item:
                        detail_items.append(detail_item)
                except Exception as e:
                    logger.error(f"상세 페이지 크롤링 실패 (idx: {list_item.idx}): {str(e)}")
        
        logger.info(f"상세 페이지 크롤링 완료: {len(detail_items)}개 성공")
        return detail_items
    
    def _fetch_detail(self, list_item: ListItem) -> DetailItem:
        """단일 상세 페이지 크롤링"""
        try:
            # 타입에 맞는 크롤러 생성
            crawler = self.factory.create_crawler(list_item.pastreqType)
            
            # 상세 페이지 요청
            params = {"idx": list_item.idx}
            response = crawler.session.post(DETAIL_URL, data=params)
            response.raise_for_status()
            
            # HTML 파싱 및 처리
            soup = BeautifulSoup(response.text, 'html.parser')
            detail_item = crawler.parse(soup, list_item.title, list_item.idx)
            
            delay(self.delay_seconds)
            return detail_item
            
        except Exception as e:
            logger.error(f"상세 페이지 요청 실패 (idx: {list_item.idx}): {str(e)}")
            return None