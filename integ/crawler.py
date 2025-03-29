"""
통합회신사례 크롤러 구현
"""
import concurrent.futures
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationCrawler:
    """금융위원회 통합회신사례 크롤러"""
    
    BASE_URL = "https://www.fsc.go.kr/po040000/listSaved"
    DETAIL_URL = "https://www.fsc.go.kr/po040000/detailSaved"
    
    def __init__(self, batch_size: int = 1000, max_items: Optional[int] = None, 
                 delay_seconds: float = 0.5, max_workers: int = 10):
        """
        크롤러 초기화
        
        Args:
            batch_size: 한 번에 요청할 목록 항목 수
            max_items: 최대 크롤링 항목 수 (None이면 모든 항목)
            delay_seconds: 상세 요청 간 지연 시간 (초)
            max_workers: 병렬 처리 시 최대 worker 수
        """
        self.batch_size = batch_size
        self.max_items = max_items
        self.delay_seconds = delay_seconds
        self.max_workers = max_workers
        self.session = requests.Session()
        
    def run(self, start_date: str, end_date: Optional[str] = None, 
            output_file: Optional[str] = None) -> pd.DataFrame:
        """
        크롤링 실행
        
        Args:
            start_date: 조회 시작일 (YYYY-MM-DD 형식)
            end_date: 조회 종료일 (YYYY-MM-DD 형식, None이면 오늘)
            output_file: 결과를 저장할 파일 경로
            
        Returns:
            수집된 데이터 DataFrame
        """
        # 날짜 설정
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"크롤링 시작: {start_date} ~ {end_date}")
        
        # 목록 데이터 수집
        list_data = self._fetch_list(start_date, end_date)
        total_count = len(list_data)
        logger.info(f"총 {total_count}개의 항목을 찾았습니다.")
        
        if self.max_items is not None and total_count > self.max_items:
            list_data = list_data[:self.max_items]
            logger.info(f"설정에 따라 {len(list_data)}개 항목으로 제한합니다.")
        
        # 상세 데이터 수집
        results = self._fetch_details(list_data)
        
        # DataFrame 변환
        df = pd.DataFrame(results)
        
        # 결과 저장
        if output_file:
            directory = os.path.dirname(output_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            ext = os.path.splitext(output_file)[1].lower()
            if ext == '.csv':
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
            elif ext in ['.xlsx', '.xls']:
                df.to_excel(output_file, index=False)
            else:
                df.to_csv(output_file if ext else f"{output_file}.csv", 
                          index=False, encoding='utf-8-sig')
            logger.info(f"결과가 {output_file}에 저장되었습니다.")
        
        return df

    def _fetch_list(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """목록 데이터 수집"""
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 날짜 형식 변환
        start_date_fmt = start_dt.strftime('%Y.%m.%d')
        end_date_fmt = end_dt.strftime('%Y.%m.%d')
        
        list_data = []
        page = 1
        
        while True:
            logger.info(f"목록 페이지 {page} 요청 중...")
            
            payload = {
                "subject": "",
                "nkeyword": "",
                "imgsdate": start_date_fmt,
                "imgnoticedat": end_date_fmt,  
                "itemPerPage": self.batch_size,  
                "curPage": page
            }
            
            response = self.session.post(self.BASE_URL, data=payload)
            if response.status_code != 200:
                logger.error(f"목록 요청 실패: 상태 코드 {response.status_code}")
                break
            
            try:
                data = response.json()
                items = data.get('list', [])
                if not items:
                    break
                    
                list_data.extend(items)
                
                # 마지막 페이지 체크
                if len(items) < self.batch_size:
                    break
                    
                page += 1
                
            except Exception as e:
                logger.error(f"목록 데이터 처리 오류: {str(e)}")
                break
                
        return list_data
        
    def _fetch_details(self, list_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """상세 데이터 수집 (병렬 처리)"""
        results = []
        total = len(list_data)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_idx = {
                executor.submit(self._fetch_detail_item, item, idx): (item, idx) 
                for idx, item in enumerate(list_data)
            }
            
            for future in concurrent.futures.as_completed(future_to_idx):
                item, idx = future_to_idx[future]
                try:
                    detail_data = future.result()
                    if detail_data:
                        # 목록 데이터와 상세 데이터 합치기
                        combined_data = {**item, **detail_data}
                        results.append(combined_data)
                    else:
                        # 상세 데이터 없으면 목록 데이터만 추가
                        results.append(item)
                    
                    logger.info(f"진행 상황: {idx+1}/{total} 완료")
                    
                except Exception as e:
                    logger.error(f"항목 {idx} 처리 중 오류: {str(e)}")
                    # 오류 발생해도 목록 데이터는 추가
                    results.append(item)
                    
        return results

    def _fetch_detail_item(self, item: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """개별 상세 페이지 수집"""
        try:
            # 지연 시간 적용
            time.sleep(self.delay_seconds)
            
            idx_no = item.get('idxNo')
            if not idx_no:
                return {}
                
            payload = {"idxNo": idx_no}
            response = self.session.post(self.DETAIL_URL, data=payload)
            
            if response.status_code != 200:
                logger.error(f"상세 요청 실패: 상태 코드 {response.status_code}, idx: {idx_no}")
                return {}
                
            try:
                data = response.json()
                detail = data.get('resultVO', {})
                
                # 본문 HTML 파싱
                content = detail.get('content', '')
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    clean_content = soup.get_text(separator='\n', strip=True)
                    detail['clean_content'] = clean_content
                    
                return detail
                
            except json.JSONDecodeError:
                logger.error(f"상세 데이터 JSON 파싱 오류, idx: {idx_no}")
                return {}
                
        except Exception as e:
            logger.error(f"상세 데이터 처리 중 오류: {str(e)}, idx: {idx_no}")
            return {}