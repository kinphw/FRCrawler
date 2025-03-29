"""
통합회신사례 목록 크롤러
"""
import logging
from datetime import datetime
from typing import List, Optional
import os
import sys
import pandas as pd

# 상위 디렉토리를 import path에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import requests
from integ.config import LIST_URL, DEFAULT_HEADERS  # 상대경로를 절대경로로 변경
from integ.models import ListItem
from integ.utils import safe_get

logger = logging.getLogger(__name__)

class ListCrawler:
    """목록 페이지 크롤러"""
    
    def __init__(self, batch_size: int = 1000):
        """
        Args:
            batch_size: 한 번에 요청할 목록 항목 수
        """
        self.batch_size = batch_size
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
    
    def crawl(self, start_date: str, end_date: Optional[str] = None) -> List[ListItem]:
        """
        목록 크롤링 실행
        
        Args:
            start_date: 조회 시작일 (YYYY-MM-DD)
            end_date: 조회 종료일 (YYYY-MM-DD, None이면 오늘)
            
        Returns:
            ListItem 객체 리스트
        """
        # 날짜 형식 변환
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_dt = datetime.now()
            
        start_date_fmt = start_dt.strftime('%Y.%m.%d')
        end_date_fmt = end_dt.strftime('%Y.%m.%d')
        
        logger.info(f"목록 크롤링 시작: {start_date_fmt} ~ {end_date_fmt}")
        
        items = []
        page = 1
        
        while True:
            logger.info(f"페이지 {page} 요청 중...")
            
            # DataTables 요청 파라미터
            params = {
                "draw": 1,
                "columns[0][data]": "rownumber",
                "columns[0][searchable]": "true",
                "columns[0][orderable]": "false",
                "columns[1][data]": "pastreqType",
                "columns[1][searchable]": "true",
                "columns[1][orderable]": "false",
                "columns[2][data]": "title",
                "columns[2][searchable]": "true",
                "columns[2][orderable]": "false",
                "columns[3][data]": "replyRegDate",
                "columns[3][searchable]": "true",
                "columns[3][orderable]": "false",
                "order[0][column]": 0,
                "order[0][dir]": "asc",
                "start": (page - 1) * self.batch_size,
                "length": self.batch_size,
                "search[value]": "",
                "searchKeyword": "",
                "searchCondition": "",
                "searchType": ""
            }
            
            try:
                response = self.session.post(LIST_URL, data=params)  # POST 요청 유지
                response.raise_for_status()
                
                data = response.json()
                list_data = data.get('data', [])  # 'list' 대신 'data' 키 사용
                
                if not list_data:
                    break
                    
                # ListItem 객체로 변환
                for item in list_data:
                    items.append(ListItem(
                        dataIdx=int(safe_get(item, 'dataIdx', default=0)),  # 필드명 수정
                        pastreqType=safe_get(item, 'pastreqType', default=''),  # 필드명 수정
                        title=safe_get(item, 'title', default=''),
                        replyRegDate=safe_get(item, 'replyRegDate', default='')  # 필드명 수정
                    ))
                
                # 마지막 페이지 체크
                total_records = int(data.get('recordsTotal', 0))
                if (page - 1) * self.batch_size + len(list_data) >= total_records:
                    break
                    
                page += 1
                
            except Exception as e:
                logger.error(f"목록 페이지 {page} 요청 실패: {str(e)}")
                logger.error(f"Response content: {response.text if 'response' in locals() else 'No response'}")
                break
        
        logger.info(f"총 {len(items)}개의 항목을 찾았습니다.")
        return items

if __name__ == "__main__":
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
    try:
        items = crawler.crawl(start_date=start_date, end_date=end_date)
        
        # 결과 출력
        print("\n=== 크롤링 결과 ===")
        print(f"총 {len(items)}개 항목 수집")
        print("\n처음 5개 항목:")
        for item in items[:5]:
            print(f"- [{item.replyRegDate}] {item.title} ({item.pastreqType})")

        # DataFrame으로 변환하여 pickle로 저장
        df = pd.DataFrame([item.__dict__ for item in items])
        df.to_pickle('list_items.pkl')    
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {str(e)}")