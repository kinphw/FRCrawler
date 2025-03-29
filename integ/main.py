"""
통합회신사례 크롤러 실행 스크립트
"""
import argparse
import logging
import os
import sys
from datetime import datetime
import concurrent.futures
from bs4 import BeautifulSoup  # 추가

import pandas as pd

# 상위 디렉토리를 import path에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from integ.list_crawler import ListCrawler
from integ.detail.factory import DetailCrawlerFactory
from integ.models import CombinedItem
from integ.utils import save_dataframe, delay

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def crawl_data(start_date: str, end_date: str = None, max_items: int = None, 
               batch_size: int = 1000, delay_time: float = 0.5, workers: int = 10):
    """
    실제 크롤링 비즈니스 로직
    """
    # 1. 목록 크롤러 실행
    logger.info(f"크롤링 시작: {start_date} ~ {end_date}")
    list_crawler = ListCrawler(batch_size=batch_size)
    list_items = list_crawler.crawl(start_date, end_date)
    
    # 최대 항목 수 제한
    if max_items:
        list_items = list_items[:max_items]
        logger.info(f"최대 항목 수 제한으로 {max_items}개만 처리합니다.")
    
    # 2. 상세 크롤링 실행
    logger.info(f"상세 페이지 크롤링 시작: {len(list_items)}개 항목")
    factory = DetailCrawlerFactory()
    detail_items = []
    
    def process_item(list_item):
        try:
            crawler = factory.create_crawler(list_item.gubun)
            params = {"idx": list_item.idx}
            response = crawler.session.post(crawler.DETAIL_URL, data=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            detail_item = crawler.parse(soup, list_item.title, list_item.idx)
            
            delay(delay_time)
            return detail_item
        except Exception as e:
            logger.error(f"상세 페이지 크롤링 실패 (idx: {list_item.idx}): {str(e)}")
            return None
    
    # 병렬 처리로 상세 정보 수집
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_item = {
            executor.submit(process_item, item): item for item in list_items
        }
        
        for future in concurrent.futures.as_completed(future_to_item):
            list_item = future_to_item[future]
            try:
                detail_item = future.result()
                if detail_item:
                    detail_items.append(detail_item)
            except Exception as e:
                logger.error(f"상세 페이지 처리 실패 (idx: {list_item.idx}): {str(e)}")
    
    # 3. 결과 통합
    combined_items = []
    for list_item, detail_item in zip(list_items, detail_items):
        if detail_item:  # 상세 정보 수집 성공한 경우만
            combined_items.append(
                CombinedItem.from_items(list_item, detail_item)
            )
    
    logger.info(f"상세 페이지 크롤링 완료: {len(combined_items)}/{len(list_items)}개 성공")
            
    # 4. DataFrame 변환
    df = pd.DataFrame([vars(item) for item in combined_items])
    
    return df

def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(description='금융위원회 통합회신사례 크롤러')
    
    parser.add_argument('-s', '--start-date', type=str, default='2023-01-01',
                        help='조회 시작일 (YYYY-MM-DD 형식)')
    parser.add_argument('-e', '--end-date', type=str, default=None,
                        help='조회 종료일 (YYYY-MM-DD 형식, 기본값: 오늘)')
    parser.add_argument('-m', '--max-items', type=int, default=None,
                        help='최대 크롤링 항목 수')
    parser.add_argument('-b', '--batch-size', type=int, default=1000,
                        help='한 번에 요청할 목록 항목 수')
    parser.add_argument('-d', '--delay', type=float, default=0.5,
                        help='상세 요청 간 지연 시간 (초)')
    parser.add_argument('-w', '--workers', type=int, default=10,
                        help='병렬 처리 시 최대 worker 수')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='결과를 저장할 파일 경로')
    
    args = parser.parse_args()
    
    try:
        df = crawl_data(
            start_date=args.start_date,
            end_date=args.end_date,
            max_items=args.max_items,
            batch_size=args.batch_size,
            delay_time=args.delay,
            workers=args.workers
        )
        
        if args.output:
            save_dataframe(df, args.output)
            logger.info(f"결과가 {args.output}에 저장되었습니다.")
            
    except KeyboardInterrupt:
        logger.info("\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()