"""
유틸리티 함수 모듈
"""

import re
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def html_to_text_preserve_p_br(html_snippet):
    """
    <p>와 <br>만 개행(\n)으로 치환하고,
    그 외 모든 태그는 제거(태그 안 텍스트는 남김).
    """
    if not html_snippet:
        return ""
    
    try:
        # 1) <p ...> => '\n'
        text = re.sub(r'<p[^>]*>', '\n', html_snippet, flags=re.IGNORECASE)
        # 2) </p> => '' (굳이 라인브레이크를 중복해서 넣지 않음)
        text = re.sub(r'</p\s*>', '', text, flags=re.IGNORECASE)

        # 3) <br ...> => '\n'
        text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)

        # 4) 그 외 모든 태그 제거 (안의 텍스트는 남김)
        #    예: <span>TEXT</span> -> "TEXT"
        text = re.sub(r'<[^<]*?>', '', text, flags=re.DOTALL)
        
        # 특수 마크업 및 메타데이터 제거
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        text = re.sub(r'<!\[CDATA\[.*?\]\]>', '', text, flags=re.DOTALL)

        # 5) 연속 개행 \n\n\n... -> \n
        text = re.sub(r'\n+', '\n', text)

        # 마무리
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