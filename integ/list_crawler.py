"""
목록 페이지 크롤링 클래스
"""
import requests
import json
import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from integ.config import (
    LIST_URL, DEFAULT_HEADERS, DEFAULT_BATCH_SIZE, 
    DEFAULT_LIST_PARAMS, GUBUN_MAPPING, DEFAULT_DELAY
)
from integ.models import ListItem
from integ.utils import random_sleep

logger = logging.getLogger(__name__)

class ListCrawler:
    """금융위원회 통합회신사례 목록 크롤러"""

    def __init__(self, batch_size: int = DEFAULT_BATCH_SIZE, max_items: Optional[int] = None):
        """
        Args:
            batch_size: 한 번에 요청할 항목 수
            max_items: 최대 크롤링할 항목 수
        """
        self.batch_size = batch_size
        self.max_items = max_items
        self.headers = DEFAULT_HEADERS.copy()
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_list_dataframe(self, start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        목록 항목을 DataFrame으로 반환
        
        Args:
            start_date: 조회 시작일 (YYYY-MM-DD 형식)
            end_date: 조회 종료일 (YYYY-MM-DD 형식, 기본값: 현재 날짜)
            
        Returns:
            수집된 목록 항목이 포함된 DataFrame
        """
        # 목록 항목 가져오기
        items = self.get_list_items(start_date, end_date)
        
        if not items:
            logger.warning("조회 결과가 없습니다.")
            return pd.DataFrame()
            
        # ListItem 객체를 DataFrame으로 직접 변환 (to_dict 메서드 활용)
        items_dict = [item.to_dict() for item in items]
            
        # DataFrame 생성
        df = pd.DataFrame(items_dict)
        return df

    def get_list_items(self, start_date: str, end_date: Optional[str] = None) -> List[ListItem]:
        """
        날짜 범위에 해당하는 목록 항목 가져오기
        
        Args:
            start_date: 조회 시작일 (YYYY-MM-DD 형식)
            end_date: 조회 종료일 (YYYY-MM-DD 형식, 기본값: 현재 날짜)
            
        Returns:
            ListItem 객체 목록
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # logger.info(f"목록 조회 기간: {start_date} ~ {end_date}")
        logger.info("목록 조회기간은 통합조회에서는 영향이 없습니다.")
        
        # 요청 파라미터 기본값 복사
        params = DEFAULT_LIST_PARAMS.copy()
        
        # 날짜 및 배치 크기 설정 업데이트
        params.update({
            "length": str(self.batch_size),
            # "searchStartDt": start_date.replace("-", ""),
            # "searchEndDt": end_date.replace("-", ""),
            # 참고로 실제 웹 요청 payload는 searchType이 전부임. 이게 뭐냐에 따라서 결과가 바뀜 (웃긴게 날짜는 영향이 없음)
        })
        
        # 요청 파라미터
        start_idx = 0
        collected_items = []
        total_count = None
        
        # 데이터 페이징 처리
        while True:
            # 시작 인덱스 업데이트
            params["start"] = str(start_idx)
            
            try:
                logger.info(f"목록 요청: start={start_idx}, length={self.batch_size}")
                response = self.session.post(LIST_URL, data=params)
                response.raise_for_status()
                
                # JSON 응답 파싱
                data = json.loads(response.text)
                
                # 처음 요청시 총 항목 수 확인
                if total_count is None:
                    total_count = data.get("recordsTotal", 0)
                    logger.info(f"총 항목 수: {total_count}")
                    
                    # 최대 항목 수 제한 적용
                    if self.max_items and self.max_items < total_count:
                        logger.info(f"최대 {self.max_items}개 항목으로 제한합니다 (전체: {total_count})")
                        total_count = self.max_items
                
                # 응답 데이터 추출
                items_data = data.get("data", [])
                if not items_data:
                    logger.debug("더 이상 항목이 없습니다.")
                    break
                    
                logger.debug(f"수신 항목 수: {len(items_data)}")
                
                # ListItem 객체로 변환하여 추가
                for item_data in items_data:
                    list_item = ListItem.from_dict(item_data)
                    collected_items.append(list_item)
                    
                    # 최대 항목 수 도달 시 중단
                    if self.max_items and len(collected_items) >= self.max_items:
                        logger.info(f"최대 항목 수({self.max_items})에 도달했습니다.")
                        break
                
                # 다음 페이지 설정 및 종료 조건 확인
                start_idx += len(items_data)
                if start_idx >= total_count or (self.max_items and len(collected_items) >= self.max_items):
                    break
                
                # 추가 요청 전 딜레이
                random_sleep(DEFAULT_DELAY)
                
            except Exception as e:
                logger.error(f"목록 요청 실패: {str(e)}")
                break
                
        logger.info(f"목록 크롤링 완료: {len(collected_items)}개 항목")
        return collected_items
    
if __name__=="__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # ListCrawler 인스턴스 생성
    crawler = ListCrawler(batch_size=1000)  # 테스트를 위해 작은 batch_size 사용
    
    # 테스트용 날짜 범위 설정 (최근 1개월)
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"테스트 기간: {start_date} ~ {end_date}")
    
    # 크롤링 실행        
    df = crawler.get_list_dataframe(start_date=start_date, end_date=end_date)  
    
    import pandasgui as pg
    pg.show(df)

    # df.to_pickle('list_items.pkl')
