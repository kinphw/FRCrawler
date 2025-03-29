"""
크롤링 실행 메인 모듈 : 과거 회신사례(2014년 이전)
v0.0.1 : 250326
"""

import argparse
import time
import pandas as pd
from datetime import datetime
import os
import sys
import pickle
import traceback

from past.list_crawler import ListCrawler
from past.detail_crawler import DetailCrawler
from past.config import OUTPUT_EXCEL

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
    parser.add_argument("--output", type=str, default=None,
                        help="결과 저장 엑셀 파일 경로 (입력하지 않으면 실행 시 물어봄)")
    parser.add_argument("--list-only", action="store_true",
                        help="목록만 크롤링 (상세 내용 생략)")
    parser.add_argument("--max-workers", type=int, default=64,
                        help="상세 내용 크롤링 시 병렬 처리 작업자 수")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="요청 간 지연 시간 (초)")
    parser.add_argument("--no-prompt", action="store_true",
                        help="파일명 입력 프롬프트 없이 기본값 사용")
    parser.add_argument("--load-pickle", type=str, default=None,
                        help="크롤링 대신 저장된 pickle 파일에서 데이터 로드")
    parser.add_argument("--show-gui", action="store_true",
                        help="결과를 pandas GUI로 표시")        

    return parser.parse_args()

def get_output_filename(default_filename, no_prompt=False):
    """사용자에게 출력 파일명을 물어보거나 기본값 사용"""
    if no_prompt:
        return default_filename
        
    try:
        user_input = input(f"저장할 파일명을 입력하세요 [기본값: {default_filename}]: ").strip()
        if not user_input:
            return default_filename
            
        # 확장자 확인 및 추가
        if not user_input.lower().endswith('.xlsx'):
            user_input += '.xlsx'
            
        return user_input
    except KeyboardInterrupt:
        print("\n취소되었습니다. 기본값을 사용합니다.")
        return default_filename

def save_to_pickle(data, base_filename):
    """데이터프레임을 pickle 파일로 저장"""
    pickle_filename = f"{os.path.splitext(base_filename)[0]}.pkl"
    with open(pickle_filename, 'wb') as f:
        pickle.dump(data, f)
    print(f"데이터 백업 저장 완료: {pickle_filename}")
    return pickle_filename

def load_from_pickle(pickle_filename):
    """pickle 파일에서 데이터프레임 로드"""
    try:
        with open(pickle_filename, 'rb') as f:
            data = pickle.load(f)
        print(f"pickle 파일에서 데이터 로드 완료: {pickle_filename}")
        return data
    except Exception as e:
        print(f"pickle 파일 로드 오류: {str(e)}")
        return None

def save_to_excel(df, output_file):
    """데이터프레임을 엑셀로 저장 (에러 처리 포함)"""
    try:
        # 엑셀 저장 전에 텍스트 데이터 정리
        for col in df.columns:
            if df[col].dtype == 'object':  # 문자열 컬럼만 처리
                # None 값을 빈 문자열로 변환
                df[col] = df[col].fillna('')
                
                # 불법 XML 문자 제거 함수
                def clean_illegal_chars(text):
                    if not isinstance(text, str):
                        return text
                    
                    # XML 1.0 사양에서 유효한 문자만 유지 (특수문자, 이모지 등 제거)
                    # XML 1.0에서 허용하는 문자: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
                    import re
                    
                    # 모든 불법 XML 문자를 공백으로 대체
                    text = re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]', ' ', text)
                    
                    return text
                
                # 불법 문자 정리
                df[col] = df[col].apply(clean_illegal_chars)
                
                # 너무 긴 텍스트 잘라내기 (엑셀 셀 제한)
                df[col] = df[col].apply(lambda x: x[:32700] if isinstance(x, str) and len(x) > 32700 else x)
                
        # 엑셀로 저장
        df.to_excel(output_file, index=False)
        print(f"크롤링 결과 저장 완료: {output_file} ({len(df)}개 항목)")
        return True
    except Exception as e:
        print(f"엑셀 저장 오류: {str(e)}")
        print(traceback.format_exc())
        return False

def main():
    """메인 실행 함수"""
    try:
        args = parse_args()
        
        # 파일명 결정
        output_file = args.output
        if output_file is None:
            output_file = get_output_filename(OUTPUT_EXCEL, args.no_prompt)
            
        start_time = time.time()
        print(f"크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # pickle 파일에서 불러오기
        if args.load_pickle:
            df = load_from_pickle(args.load_pickle)
            if df is not None:
                save_to_excel(df, output_file)
                elapsed_time = time.time() - start_time
                hours, remainder = divmod(elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"작업 완료: 총 소요 시간 {int(hours)}시간 {int(minutes)}분 {seconds:.1f}초")
                return
            else:
                print("pickle 파일 로드 실패, 크롤링을 시작합니다.")
        
        # 목록 크롤링
        list_crawler = ListCrawler(batch_size=args.batch_size, max_items=args.max_items)
        list_items = list_crawler.get_list_items(start_date=args.start_date, end_date=args.end_date)
        
        if not list_items:
            print("목록 크롤링 결과가 없습니다.")
            return
        
        if args.list_only:
            # 목록만 저장
            list_df = pd.DataFrame([vars(item) for item in list_items])
            # 항상 pickle로 먼저 저장
            save_to_pickle(list_df, output_file)
            # 엑셀 저장
            save_to_excel(list_df, output_file)
        else:
            # 상세 내용 크롤링 및 결합
            detail_crawler = DetailCrawler(delay_seconds=args.delay, max_workers=args.max_workers)
            combined_df = detail_crawler.get_combined_dataframe(list_items)
            
            # 항상 pickle로 먼저 저장
            pickle_file = save_to_pickle(combined_df, output_file)
            
            # 결과 저장
            if not save_to_excel(combined_df, output_file):
                print(f"엑셀 저장에 실패했습니다. 데이터는 {pickle_file}에 백업되어 있습니다.")
                print(f"다음 명령어로 pickle 파일에서 데이터를 복구할 수 있습니다:")
                print(f"python -m past.main --load-pickle {pickle_file} --output {output_file}")
        
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"크롤링 완료: 총 소요 시간 {int(hours)}시간 {int(minutes)}분 {seconds:.1f}초")

        # GUI 표시 옵션이 있는 경우
        if args.show_gui and combined_df is not None:
            try:
                from pandasgui import show
                print("pandas GUI를 실행합니다...")
                show(combined_df)
            except ImportError:
                print("pandasgui 패키지가 설치되어 있지 않습니다.")
                print("설치하려면: pip install pandasgui")        

    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()