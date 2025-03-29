"""
통합회신사례 크롤러 실행 스크립트
"""

import argparse
import os
import sys
from datetime import datetime

# 상위 디렉토리를 import path에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from integ.crawler import IntegrationCrawler

def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(description='금융위원회 통합회신사례 크롤러')
    
    # 파라미터 정의
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
    
    # 크롤러 초기화 및 실행
    crawler = IntegrationCrawler(
        batch_size=args.batch_size,
        max_items=args.max_items,
        delay_seconds=args.delay,
        max_workers=args.workers
    )
    
    crawler.run(
        start_date=args.start_date,
        end_date=args.end_date,
        output_file=args.output
    )

if __name__ == "__main__":
    main()