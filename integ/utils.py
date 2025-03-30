"""
유틸리티 함수
"""
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


def random_sleep(base_seconds: float = 0.3, jitter: float = 0.2) -> None:
    """지연 시간에 변동을 주어 봇 탐지 회피"""
    jitter_value = random.uniform(-jitter, jitter)
    sleep_time = max(0.1, base_seconds + jitter_value)
    time.sleep(sleep_time)

def clean_text(text: str) -> str:
    """텍스트 정리 (HTML 태그 제거, 공백 정리 등)"""
    if not text:
        return ""
    
    import re
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', ' ', text)
    # 연속된 공백 문자를 하나로
    text = re.sub(r'\s+', ' ', text)
    
    text = html.unescape(text)  # HTML 엔티티 변환
    
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