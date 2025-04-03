"""
통합회신사례 크롤링 메인 모듈 : "현장건의 과제" 만 처리리
"""
import argparse
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd

from integ.list_crawler import ListCrawler
from integ.detail_crawler import DetailCrawler
from integ.config import DEFAULT_DELAY, DEFAULT_MAX_WORKERS, DEFAULT_BATCH_SIZE

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def parse_args():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(description="금융위원회 통합회신사례 크롤러")
    
    parser.add_argument("--start-date", type=str, default="2000-01-01",
                        help="크롤링 시작일 (YYYY-MM-DD 형식)")
    parser.add_argument("--end-date", type=str, default=None,
                        help="크롤링 종료일 (YYYY-MM-DD 형식, 기본값: 오늘)")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                        help="한 번에 요청할 항목 수")
    parser.add_argument("--max-items", type=int, default=None,
                        help="최대 크롤링할 항목 수")
    parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS,
                        help="상세 내용 크롤링 시 병렬 처리 작업자 수")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                        help="요청 간 지연 시간 (초)")
    parser.add_argument("--gubun-codes", type=int, nargs='+',
                        help="처리할 문서 유형 코드 (1:법령해석, 2:비조치의견서, 3:현장점검의견, 4:과거회신사례)")
    
    return parser.parse_args()

def main(start_date: str = "2000-01-01", end_date: Optional[str] = None, 
         batch_size: int = DEFAULT_BATCH_SIZE, max_items: Optional[int] = None, 
         max_workers: int = DEFAULT_MAX_WORKERS, delay: float = DEFAULT_DELAY
         ) -> pd.DataFrame:
    """
    메인 실행 함수 - 순수 데이터 조회 기능만 제공
    
    Args:
        start_date: 조회 시작일 (기본값: "2000-01-01")
        end_date: 조회 종료일 (기본값: 현재 날짜)
        batch_size: 한 번에 요청할 항목 수 (기본값: 기본값 사용)
        max_items: 최대 크롤링 항목 수 (기본값: 제한 없음)
        max_workers: 병렬 처리 작업자 수 (기본값: 기본값 사용)
        delay: 요청 간 지연 시간 초 (기본값: 기본값 사용)        
        
    Returns:
        문서 유형별 결과 데이터프레임 딕셔너리
    """
    # try:
    start_time = time.time()
    logger.info(f"통합회신사례 크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 목록 크롤링
    logger.info(f"목록 크롤링 시작: {start_date} ~ {end_date or '현재'}")
    list_crawler = ListCrawler(batch_size=batch_size, max_items=max_items)
    # list_df = list_crawler.get_list_dataframe(start_date=start_date, end_date=end_date)
    list_combined = list_crawler.get_list_items(start_date=start_date, end_date=end_date)
    
    # if list_df.empty:
    #     logger.warning("목록 크롤링 결과가 없습니다.")
    #     return {}
    
    logger.info(f"목록 크롤링 완료: 총 {len(list_combined)}개 항목")
    
    # 2. 상세 페이지 크롤링
    # 다 삭제하고 "현장건의 과제"만 추출할 것임    
    detail_crawler = DetailCrawler(delay_seconds=delay, max_workers=max_workers)
    result_df = detail_crawler.get_combined_dataframe(list_combined)
    
    # 3. 소요 시간 및 결과 통계 출력
    elapsed_time = time.time() - start_time
    from common.utils import format_elapsed_time
    logger.info(f"크롤링 완료: 총 소요 시간 {format_elapsed_time(elapsed_time)}")
    
    # 결과 통계
    if not result_df.empty:
        total_items = result_df.shape[0]
        logger.info(f"총 결과 항목: {total_items}개")
    
    return result_df
        
    # except KeyboardInterrupt:
    #     logger.info("사용자에 의해 중단되었습니다.")
    #     return {}
    # except Exception as e:
    #     logger.error(f"크롤링 중 오류 발생: {str(e)}")
    #     logger.debug(traceback.format_exc())
    #     return {}

if __name__ == "__main__":
    args = parse_args()
    
    # 명령행에서 실행 시 결과 저장 옵션 처리
    result_df:pd.DataFrame = main(
        start_date=args.start_date,
        end_date=args.end_date,
        batch_size=args.batch_size,
        max_items=args.max_items,
        max_workers=args.max_workers,
        delay=args.delay        
    )
        
    import pandasgui as pg
    pg.show(result_df)