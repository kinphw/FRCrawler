"""
상세 페이지 크롤러 기본 클래스
"""
from abc import ABC, abstractmethod
import logging
from bs4 import BeautifulSoup

from ..config import DETAIL_URL, DEFAULT_HEADERS
from ..models import DetailItem
from ..utils import get_td_html_after_th, html_to_text_preserve_p_br

logger = logging.getLogger(__name__)

class BaseDetailCrawler(ABC):
    """상세 페이지 크롤러 추상 클래스"""
    
    def __init__(self, session):
        """
        Args:
            session: 요청에 사용할 session 객체
        """
        self.session = session
        
    @abstractmethod
    def parse(self, soup: BeautifulSoup, title: str, idx: int) -> DetailItem:
        """
        상세 페이지 파싱
        
        Args:
            soup: BeautifulSoup 객체
            title: 제목
            idx: 게시물 번호
            
        Returns:
            DetailItem 객체
        """
        pass