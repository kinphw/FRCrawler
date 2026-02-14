"""
크롤러 기본 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
import time
import re
from bs4 import BeautifulSoup

from late.models import DetailItem
from common.utils import random_sleep, html_to_text_preserve_p_br
from common.ssl_adapter import get_legacy_session

class BaseFetcher(ABC):
    """HTML 페이지 요청 기본 클래스"""
    
    def __init__(self, delay_seconds: float = 0.5):
        """
        Args:
            delay_seconds: 요청 간 지연 시간 (초)
        """
        self.delay_seconds = delay_seconds
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = get_legacy_session()
    
    def fetch(self, idx: int) -> Optional[str]:
        """
        상세 내용 HTML을 요청하여 반환 (템플릿 메서드)
        
        Args:
            idx: 상세화면 idx
            
        Returns:
            HTML 문자열, 오류 시 None
        """
        try:
            url = self._get_url()
            params = self._get_request_params(idx)
            
            response = self.session.post(url, headers=self.headers, data=params) #던진다!
            response.raise_for_status()
            
            # 너무 빠른 연속 요청 방지
            random_sleep(self.delay_seconds)
            
            return response.text
        except Exception:
            return None
            
    @abstractmethod
    def _get_url(self) -> str:
        """요청 URL 반환 (하위 클래스에서 구현)"""
        pass
        
    @abstractmethod
    def _get_request_params(self, idx: int) -> dict:
        """요청 파라미터 반환 (하위 클래스에서 구현)"""
        pass
