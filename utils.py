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
    
    # 1) <p ...> => '\n'
    text = re.sub(r'<p[^>]*>', '\n', html_snippet, flags=re.IGNORECASE)
    # 2) </p> => '' (굳이 라인브레이크를 중복해서 넣지 않음)
    text = re.sub(r'</p\s*>', '', text, flags=re.IGNORECASE)

    # 3) <br ...> => '\n'
    text = re.sub(r'<br[^>]*>', '\n', text, flags=re.IGNORECASE)

    # 4) 그 외 모든 태그 제거 (안의 텍스트는 남김)
    #    예: <span>TEXT</span> -> "TEXT"
    text = re.sub(r'<.*?>', '', text, flags=re.DOTALL)

    # 5) 연속 개행 \n\n\n... -> \n
    text = re.sub(r'\n+', '\n', text)

    # 마무리
    return text.strip()

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
    th_tag = soup.find("th", string=lambda x: x and x.strip() == th_text)
    if not th_tag:
        return None
    td_tag = th_tag.find_next("td")
    return str(td_tag) if td_tag else None