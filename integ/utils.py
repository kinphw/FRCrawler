"""
통합회신사례 크롤링 유틸리티 함수
"""
from bs4 import BeautifulSoup
import pandas as pd
import time
from typing import Optional, Dict, Any

def get_td_html_after_th(soup: BeautifulSoup, th_text: str) -> Optional[str]:
    """
    테이블에서 특정 th 텍스트 다음에 오는 td의 HTML을 반환
    
    Args:
        soup: BeautifulSoup 객체
        th_text: 찾을 th 텍스트
    
    Returns:
        td의 HTML 문자열 또는 None
    """
    th = soup.find('th', string=lambda x: x and th_text in x)
    if th and th.find_next('td'):
        return str(th.find_next('td'))
    return None

def html_to_text_preserve_p_br(html: Optional[str]) -> Optional[str]:
    """
    HTML을 텍스트로 변환하되 <p>와 <br> 태그는 개행으로 처리
    
    Args:
        html: HTML 문자열
        
    Returns:
        변환된 텍스트 또는 None
    """
    if not html:
        return None
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # <br>, <p> 태그를 개행문자로 변경
    for tag in soup.find_all(['br', 'p']):
        tag.replace_with('\n' + tag.get_text())
    
    # 텍스트 정리
    text = soup.get_text()
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    
    return text if text else None

def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    중첩된 딕셔너리에서 안전하게 값을 가져오는 함수
    
    Args:
        data: 딕셔너리
        keys: 순차적으로 접근할 키들
        default: 값이 없을 경우 반환할 기본값
    """
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data

def save_dataframe(df: pd.DataFrame, output_file: str):
    """
    DataFrame을 파일로 저장
    
    Args:
        df: 저장할 DataFrame
        output_file: 저장할 파일 경로 (.csv 또는 .xlsx)
    """
    ext = output_file.lower().split('.')[-1]
    
    if ext == 'csv':
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    elif ext in ['xlsx', 'xls']:
        df.to_excel(output_file, index=False, engine='openpyxl')
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {ext}")

def delay(seconds: float):
    """
    지정된 시간만큼 지연
    
    Args:
        seconds: 지연할 시간(초)
    """
    time.sleep(seconds)