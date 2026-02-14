"""
목록 크롤링 클래스
"""

import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from late.models import ListItem
from late.config import LIST_URL, DEFAULT_HEADERS
from common.utils import random_sleep
from common.ssl_adapter import get_legacy_session

class ListCrawler:
    """금융위원회 회신사례 목록 크롤러"""
    
    def __init__(self, batch_size: int = 1000, max_items: Optional[int] = None):
        """
        Args:
            batch_size: 한 번에 요청할 항목 수
            max_items: 최대 크롤링할 항목 수 (None이면 전체)
        """
        self.batch_size = batch_size
        self.max_items = max_items
        self.headers = DEFAULT_HEADERS.copy()
        self.session = get_legacy_session()
        
    def get_list_items(self, start_date: str = "2000-01-01", end_date: Optional[str] = None) -> List[ListItem]:
        """
        목록 아이템을 크롤링하여 반환
        
        Args:
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD), None이면 오늘 날짜
            
        Returns:
            목록 아이템 리스트
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
            
        all_items = []
        start_pos = 0
        total_count = None
        
        print(f"목록 크롤링 시작: {start_date} ~ {end_date}")
        
        while True:
            # 최대 아이템 수 제한 확인
            if self.max_items and start_pos >= self.max_items:
                break
                
            # 배치 크기 조정 (max_items가 지정된 경우)
            current_batch_size = self.batch_size
            if self.max_items and start_pos + current_batch_size > self.max_items:
                current_batch_size = self.max_items - start_pos
                
            # API 요청 데이터
            data = {
                "draw": 1,
                "start": start_pos,
                "length": current_batch_size,
                "searchReplyRegDateStart": start_date,
                "searchReplyRegDateEnd": end_date
            }
            
            response = self.session.post(LIST_URL, headers=self.headers, data=data)
            json_data = response.json()
            
            # 첫 번째 요청에서 전체 개수 확인
            if total_count is None:
                total_count = json_data.get("recordsTotal", 0)
                print(f"전체 항목 수: {total_count}")
                
                # 최대 아이템 수 조정
                if self.max_items is None or self.max_items > total_count:
                    self.max_items = total_count
            
            # 결과가 없으면 종료
            batch_items = json_data.get("data", [])
            if not batch_items:
                break
                
            # 목록 아이템 변환 및 추가
            for item in batch_items:
                list_item = ListItem(
                    rownumber=item.get("rownumber", 0),
                    idx=item.get("idx", 0),
                    gubun=item.get("gubun", ""),
                    category=item.get("category", None),
                    title=item.get("title", ""),
                    regDate=item.get("regDate", ""),
                    number=item.get("number", "")
                )
                all_items.append(list_item)
                
            # 진행 상황 출력
            print(f"목록 진행: {start_pos + len(batch_items)}/{self.max_items} 항목 크롤링 완료")
            
            # 다음 배치로 이동
            start_pos += current_batch_size
            
            # 전체 항목 수에 도달하면 종료
            if start_pos >= total_count:
                break
                
            # 요청 간 지연
            random_sleep()
            
        print(f"목록 크롤링 완료: 총 {len(all_items)}개 항목")
        return all_items
        
    def get_list_dataframe(self, start_date: str = "2000-01-01", end_date: Optional[str] = None) -> pd.DataFrame:
        """
        목록을 데이터프레임으로 반환
        """
        list_items = self.get_list_items(start_date, end_date)
        return pd.DataFrame([vars(item) for item in list_items])
    
if __name__ == "__main__":
    crawler = ListCrawler(batch_size=1000)
    df = crawler.get_list_dataframe(start_date="2000-01-01", end_date="2025-03-31")
    import pandasgui as pg
    pg.show(df)