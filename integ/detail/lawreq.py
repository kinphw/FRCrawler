"""
법령해석 상세 페이지 크롤러
"""
import logging
from bs4 import BeautifulSoup

from .base import BaseDetailCrawler
from ..models import DetailItem
from ..utils import get_td_html_after_th, html_to_text_preserve_p_br

logger = logging.getLogger(__name__)

class LawreqDetailCrawler(BaseDetailCrawler):
    """법령해석 상세 페이지 크롤러"""
    
    def parse(self, soup: BeautifulSoup, title: str, idx: int) -> DetailItem:
        """법령해석 상세 페이지 파싱"""
        try:
            # 신청인
            registrant_html = get_td_html_after_th(soup, "신청인")
            registrant = html_to_text_preserve_p_br(registrant_html) if registrant_html else None
            
            # 회신일
            reply_date_html = get_td_html_after_th(soup, "회신일")
            reply_date = html_to_text_preserve_p_br(reply_date_html) if reply_date_html else None
            
            # 질의내용
            inquiry_html = get_td_html_after_th(soup, "질의내용")
            inquiry = html_to_text_preserve_p_br(inquiry_html) if inquiry_html else None
            
            # 회신내용
            answer_html = get_td_html_after_th(soup, "회신내용")
            answer = html_to_text_preserve_p_br(answer_html) if answer_html else None
            
            # 판단이유
            reason_html = get_td_html_after_th(soup, "판단이유")
            reason = html_to_text_preserve_p_br(reason_html) if reason_html else None
            
            return DetailItem(
                title=title,
                registrant=registrant,
                reply_date=reply_date,
                inquiry=inquiry,
                answer=answer,
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"법령해석 상세 페이지 파싱 실패 (idx: {idx}): {str(e)}")
            return None