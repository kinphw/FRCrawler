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
    HTML을 텍스트로 변환하되 단락과 줄바꿈을 보존
    
    Args:
        html_snippet: HTML 문자열
        
    Returns:
        변환된 텍스트
    """
    try:
        soup = BeautifulSoup(html_snippet, 'html.parser')
        
        # 줄바꿈 태그를 줄바꿈 문자로 대체
        for br in soup.find_all('br'):
            br.replace_with('\n')
        
        # 단락 태그 처리
        for p in soup.find_all('p'):
            p_text = p.get_text()
            p.replace_with(f"{p_text}\n\n")
        
        # 다른 태그들은 공백으로 대체하면서 텍스트 추출
        text = soup.get_text()
        
        # 연속된 줄바꿈 정리
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    except Exception as e:
        # 오류 발생 시 원본 HTML에서 가능한 많은 텍스트 추출 시도
        try:
            # 간단한 태그 제거 시도
            return re.sub(r'<[^>]*>', ' ', html_snippet).strip()
        except:
            # 완전히 실패한 경우
            return "[HTML 변환 오류]"

def random_sleep(min_seconds=1, max_seconds=3):
    """
    랜덤 시간만큼 대기 (서버 부하 방지)
    
    Args:
        min_seconds: 최소 대기 시간(초)
        max_seconds: 최대 대기 시간(초)
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def get_td_html_after_th(soup, th_text):
    """
    특정 th 텍스트를 가진 요소 다음의 td 요소의 HTML 반환
    
    Args:
        soup: BeautifulSoup 객체
        th_text: 찾을 th 텍스트
        
    Returns:
        td 요소의 HTML 문자열, 찾지 못한 경우 None
    """
    # 정확한 텍스트 매칭
    th_tag = soup.find("th", string=lambda x: x and x.strip() == th_text)
    if th_tag:
        td_tag = th_tag.find_next("td")
        if td_tag:
            return str(td_tag)
    
    # 부분 텍스트 매칭
    th_tag = soup.find("th", string=lambda x: x and th_text in x.strip())
    if th_tag:
        td_tag = th_tag.find_next("td")
        if td_tag:
            return str(td_tag)
    
    # 클래스 기반 검색
    for class_name in ["", "bc-blue", "bc-yellow"]:
        attrs = {"scope": "row"}
        if class_name:
            attrs["class"] = class_name
        
        th_tags = soup.find_all("th", attrs=attrs)
        for th in th_tags:
            if th.text.strip() == th_text:
                td_tag = th.find_next("td")
                if td_tag:
                    return str(td_tag)
    
    return None