"""
유틸리티 함수 모듈
"""

import re
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

import os
import re
import time
import html
import random
import logging
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def html_to_text_preserve_p_br(html_snippet):
    """
    <p>와 <br>만 개행(\n)으로 치환하고,
    그 외 모든 태그는 제거(태그 안 텍스트는 남김).
    """
    if not html_snippet:
        return ""
    
    try:
        # [핵심] 기존에 포함된 개행 제거 (그래야 우리가 넣는 \n만 남음)
        html_snippet = html_snippet.replace('\r', '').replace('\n', '')

        # 1) <p ...> → '\n'
        text = re.sub(r'<p[^>]*>', '\n', html_snippet, flags=re.IGNORECASE)
        # 2) </p> → ''
        text = re.sub(r'</p\s*>', '', text, flags=re.IGNORECASE)

        # 3) <br ...> → '\n'
        text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)

        # 4) 주석 및 CDATA 제거
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        text = re.sub(r'<!\[CDATA\[.*?\]\]>', '', text, flags=re.DOTALL)

        # 5) <style>, <script> 블록 제거
        text = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # 6) 나머지 모든 태그 제거
        text = re.sub(r'</?[^>]+>', '', text)

        # 7) HTML 엔티티 정리
        text = re.sub(r'&nbsp;?', ' ', text)

        # 8) 중복 개행 줄이기 전, 개행 사이 공백 제거
        # text = re.sub(r'\n\s+\n', '\n', text)
        
        # 9) 연속 개행 \n\n\n... → \n
        text = re.sub(r'\n+', '\n', text)

        return text.strip()
    except Exception as e:
        print(f"HTML 텍스트 변환 오류: {str(e)}")
        # 오류 발생 시 원본 HTML에서 가능한 많은 텍스트 추출 시도
        try:
            # 간단한 태그 제거 시도
            return re.sub(r'<[^>]*>', ' ', html_snippet).strip()
        except:
            # 완전히 실패한 경우
            return "[HTML 변환 오류]"

def random_sleep(min_seconds=1, max_seconds=3):
    """
    요청 간 랜덤 지연 시간을 추가하여 서버 부하 및 차단 방지
    """
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)
    
def get_td_html_after_th(soup, th_text):
    """
    특정 <th> 텍스트를 찾아서, 바로 옆 <td> HTML 추출
    """
    # 방법 1: 표준 텍스트 검색
    th_tag = soup.find("th", string=lambda x: x and x.strip() == th_text)
    if th_tag:
        td_tag = th_tag.find_next("td")
        return str(td_tag) if td_tag else None
        
    # 방법 2: 특수 클래스가 있는 경우 (예: "bc-blue", "bc-yellow" 클래스)
    th_tag = soup.find("th", attrs={"scope": "row"}, string=lambda x: x and x.strip() == th_text)
    if th_tag:
        td_tag = th_tag.find_next("td")
        return str(td_tag) if td_tag else None
        
    # 방법 3: 더 일반적인 검색
    all_th_tags = soup.find_all("th")
    for th in all_th_tags:
        if th.text.strip() == th_text:
            td_tag = th.find_next("td")
            return str(td_tag) if td_tag else None
            
    return None


# def random_sleep(base_seconds: float = 0.3, jitter: float = 0.2) -> None:
#     """지연 시간에 변동을 주어 봇 탐지 회피"""
#     jitter_value = random.uniform(-jitter, jitter)
#     sleep_time = max(0.1, base_seconds + jitter_value)
#     time.sleep(sleep_time)

def clean_text(text: str) -> str:
    """텍스트 정리 (HTML 태그 제거, 공백 정리 등)"""
    if not text:
        return ""
    
    text = html.unescape(text)    
    
    # HTML 태그 제거
    import re
    text = re.sub(r'<[^>]+>', ' ', text)
    # 연속된 공백 문자를 하나로
    text = re.sub(r'\s+', ' ', text)
    
    # 앞뒤 공백 제거
    return text.strip()

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """딕셔너리에서 안전하게 값 가져오기"""
    return data.get(key, default)

def format_elapsed_time(seconds: float) -> str:
    """소요 시간을 사람이 읽기 쉬운 형식으로 변환"""
    if seconds < 60:
        return f"{seconds:.1f}초"
    elif seconds < 3600:
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes)}분 {seconds:.1f}초"
    else:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}시간 {int(minutes)}분 {seconds:.1f}초"

def save_dataframe(df: pd.DataFrame, file_path: str, 
                   include_index: bool = False) -> bool:
    """데이터프레임을 파일로 저장"""
    try:
        # 파일 확장자 확인
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # 확장자별 저장 방식
        if ext == '.csv':
            df.to_csv(file_path, index=include_index, encoding='utf-8-sig')
        elif ext == '.xlsx':
            df.to_excel(file_path, index=include_index, engine='openpyxl')
        elif ext == '.pkl' or ext == '.pickle':
            df.to_pickle(file_path)
        else:
            logger.warning(f"지원하지 않는 파일 형식: {ext}, Excel(.xlsx) 형식으로 저장합니다.")
            file_path = f"{os.path.splitext(file_path)[0]}.xlsx"
            df.to_excel(file_path, index=include_index, engine='openpyxl')
        
        logger.info(f"파일 저장 완료: {file_path} ({len(df)}개 항목)")
        return True
        
    except Exception as e:
        logger.error(f"파일 저장 실패: {str(e)}")
        return False