"""
비조치의견서 상세 페이지 파싱 클래스
"""

from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from integ.detail.base_parser import BaseParser
from integ.models import DetailItem
from integ.utils import html_to_text_preserve_p_br

class OpinionParser(BaseParser):
    """비조치의견서 상세 페이지 파싱 클래스"""
    
    def parse(self, html_content: str, idx: int, gubun: str) -> DetailItem:
        """
        비조치의견서 HTML 파싱
        
        Args:
            html_content: 상세 페이지 HTML
            idx: 문서 식별자
            gubun: 문서 유형
            
        Returns:
            DetailItem 객체
        """
        # BeautifulSoup 객체 생성
        soup = self._create_soup(html_content)
        if not soup:
            return self._create_error_item()
            
        # 필수 필드 추출
        title = self._extract_title(soup)
        if not title:
            return self._create_error_item()
            
        # 비조치의견서 필드 추출 (필드명 여러 가지 시도)
        registrant = self._extract_field(soup, "등록자")
        reply_date = self._extract_field(soup, "회신일")
        inquiry = self._extract_field(soup, "질의요지")
        answer = self._extract_field(soup, "회답")
        reason = self._extract_field(soup, "이유")
        
        # 이유 필드가 없으면 정규식으로 찾기 시도
        if not reason:
            reason = self._extract_field_by_regex(html_content, "이유")
        
        # # 비조치의견서 추가 필드
        # opinion_number = self._extract_field(soup, "비조치의견서번호")
        # applicant = self._extract_field(soup, "신청인")
        
        # DetailItem 생성
        return DetailItem(
            title=title,
            registrant=registrant,
            reply_date=reply_date,
            inquiry=inquiry,
            answer=answer,
            reason=reason,
            # 추가 필드는 DetailItem 확장 시 포함
            # opinion_number=opinion_number,
            # applicant=applicant
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """비조치의견서 제목 추출"""
        try:
            # 여러 방법 시도
            # 1. 일반 제목 클래스
            title_td = soup.find("td", class_="subject")
            if title_td:
                title_html = str(title_td)
                return html_to_text_preserve_p_br(title_html)
                
            # 2. 특수 비조치의견서 제목 필드
            title_field = self._extract_field(soup, "제목") or self._extract_field(soup, "건명")
            if title_field:
                return title_field
                
            # 3. 특수 헤더 추출
            header = soup.find("div", class_="board_view_header")
            if header:
                return header.get_text(strip=True)
        except Exception:
            pass
            
        return None
    
    def _create_error_item(self) -> DetailItem:
        """파싱 오류 시 비조치의견서용 기본 DetailItem 생성"""
        return DetailItem(
            title="[비조치의견서 파싱 오류]",
            registrant=None,
            reply_date=None,
            inquiry=None,
            answer=None,
            reason=None
        )