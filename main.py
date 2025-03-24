"""
크롤링 실행 메인 모듈
"""

import argparse
import time
import pandas as pd
from datetime import datetime
import os

from list_crawler import ListCrawler
from detail_crawler import DetailCrawler
from config import OUTPUT_EXCEL

def parse_args():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(description="금융위원회 회신사례 크롤러")
    
    parser.add_argument("--start-date", type=str, default="2000-01-01",
                        help="크롤링 시작일 (YYYY-MM-DD 형식)")
    parser.add_argument("--end-date", type=str, default=None,
                        help="크롤링 종료일 (YYYY-MM-DD 형식, 기본값: 오늘)")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="한 번에 요청할 항목 수")
    parser.add_argument("--max-items", type=int, default=None,
                        help="최대 크롤링할 항목 수")
    parser.add_argument("--output", type=str, default=OUTPUT_EXCEL,
                        help="결과 저장 엑셀 파일 경로")
    parser.add_argument("--list-only", action="store_true",
                        help="목록만 크롤링 (상세 내용 생략)")
    
    return parser.parse_args()

def main():
    """메인 실행 함수"""
    args = parse_args()
    
    start_time = time.time()
    print(f"크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 목록 크롤링
    list_crawler = ListCrawler(batch_size=args.batch_size, max_items=args.max_items)
    list_items = list_crawler.get_list_items(start_date=args.start_date, end_date=args.end_date)
    
    if args.list_only:
        # 목록만 저장
        list_df = pd.DataFrame([vars(item) for item in list_items])
        list_df.to_excel(args.output, index=False)
        print(f"목록 크롤링 결과 저장 완료: {args.output} ({len(list_df)}개 항목)")
    else:
        # 상세 내용 크롤링 및 결합
        detail_crawler = DetailCrawler()
        combined_df = detail_crawler.get_combined_dataframe(list_items)
        
        # 결과 저장
        combined_df.to_excel(args.output, index=False)
        print(f"크롤링 결과 저장 완료: {args.output} ({len(combined_df)}개 항목)")
    
    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"크롤링 완료: 총 소요 시간 {int(hours)}시간 {int(minutes)}분 {seconds:.1f}초")

if __name__ == "__main__":
    main()