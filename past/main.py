"""
크롤링 실행 메인 모듈 : 과거 회신사례(2014년 이전) 
v0.0.2 : 250330
"""

import argparse
import time
import pandas as pd
from datetime import datetime
import traceback

from past.list_crawler import ListCrawler
from past.detail_crawler import DetailCrawler

def parse_args():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(description="금융위원회 과거 회신사례(2014년 이전) 크롤러")
    
    parser.add_argument("--start-date", type=str, default="2000-01-01",
                        help="크롤링 시작일 (YYYY-MM-DD 형식)")
    parser.add_argument("--end-date", type=str, default=None,
                        help="크롤링 종료일 (YYYY-MM-DD 형식, 기본값: 오늘)")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="한 번에 요청할 항목 수")
    parser.add_argument("--max-items", type=int, default=None,
                        help="최대 크롤링할 항목 수")
    parser.add_argument("--max-workers", type=int, default=8,
                        help="상세 내용 크롤링 시 병렬 처리 작업자 수")
    parser.add_argument("--delay", type=float, default=0.3,
                        help="요청 간 지연 시간 (초)")

    return parser.parse_args()

def main(start_date="2000-01-01", end_date=None, batch_size=1000, 
         max_items=None, max_workers=8, delay=0.3)-> pd.DataFrame : 
    """
    메인 실행 함수 (순수 데이터 조회 기능만 제공)
    
    Args:
        start_date: 조회 시작일 (기본값: "2000-01-01")
        end_date: 조회 종료일 (기본값: 현재 날짜)
        batch_size: 한 번에 요청할 항목 수 (기본값: 1000)
        max_items: 최대 크롤링 항목 수 (기본값: 제한 없음)
        max_workers: 병렬 처리 작업자 수 (기본값: 8)
        delay: 요청 간 지연 시간 초 (기본값: 0.3)
        
    Returns:
        pd.DataFrame: 크롤링 결과 데이터프레임
    """
    try:
        start_time = time.time()
        print(f"크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 목록 크롤링
        print(f"목록 크롤링 중... (시작일: {start_date}, 종료일: {end_date or '현재'})")
        list_crawler = ListCrawler(batch_size=batch_size, max_items=max_items)
        list_items = list_crawler.get_list_items(start_date=start_date, end_date=end_date)
        
        if not list_items:
            print("목록 크롤링 결과가 없습니다.")
            return pd.DataFrame()  # 빈 데이터프레임 반환
            
        print(f"목록 크롤링 완료: {len(list_items)}개 항목")
        
        # 상세 내용 크롤링 및 결합
        print("상세 내용 크롤링 중...")
        detail_crawler = DetailCrawler(delay_seconds=delay, max_workers=max_workers)
        result_df = detail_crawler.get_combined_dataframe(list_items)
        
        # 소요 시간 출력
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"크롤링 완료: 총 {len(result_df)}개 항목, 소요 시간 {int(hours)}시간 {int(minutes)}분 {seconds:.1f}초")
        
        # 결과 반환
        return result_df

    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print(traceback.format_exc())
        return pd.DataFrame()  # 빈 데이터프레임 반환

if __name__ == "__main__":
    args = parse_args()
    result = main(
        start_date=args.start_date,
        end_date=args.end_date,
        batch_size=args.batch_size,
        max_items=args.max_items,
        max_workers=args.max_workers,
        delay=args.delay
    )