"""
법령해석 상세 페이지 파싱 클래스
"""

from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from late.detail.base_parser import BaseParser
from late.models import DetailItem
from late.utils import html_to_text_preserve_p_br

class LawParser(BaseParser):
    """법령해석 상세 페이지 파싱 클래스"""
    
    def parse(self, html_content: str, idx: int, gubun: str) -> DetailItem:
        """
        법령해석 HTML 파싱
        
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
            
        # 법령해석 필드 추출
        registrant = self._extract_field(soup, "등록자")
        reply_date = self._extract_field(soup, "회신일")
        inquiry = self._extract_field(soup, "질의요지")
        answer = self._extract_field(soup, "회답")
        reason = self._extract_field(soup, "이유")
        
        # 이유 필드가 없으면 정규식으로 찾기 시도
        if not reason:
            reason = self._extract_field_by_regex(html_content, "이유")
            
        # 추가 필드 (향후 확장 가능)
        category = self._extract_field(soup, "분야")
        related_law = self._extract_field(soup, "관련법령")
        
        # DetailItem 생성
        return DetailItem(
            title=title,
            registrant=registrant,
            reply_date=reply_date,
            inquiry=inquiry,
            answer=answer,
            reason=reason,
            # 추가 필드는 DetailItem 확장 시 포함
            # category=category,
            # related_law=related_law
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """법령해석 제목 추출"""
        try:
            # 여러 방법 시도
            # 1. 일반 제목 클래스
            title_td = soup.find("td", class_="subject")
            if title_td:
                title_html = str(title_td)
                return html_to_text_preserve_p_br(title_html)
                
            # 2. 메타 필드에서 추출
            title_field = self._extract_field(soup, "제목")
            if title_field:
                return title_field
                
            # 3. H1/H2 태그에서 추출
            for tag in ["h1", "h2"]:
                h_tag = soup.find(tag)
                if h_tag:
                    return h_tag.get_text(strip=True)
        except Exception:
            pass
            
        return None
    
    def _create_error_item(self) -> DetailItem:
        """파싱 오류 시 법령해석용 기본 DetailItem 생성"""
        return DetailItem(
            title="[법령해석 파싱 오류]",
            registrant=None,
            reply_date=None,
            inquiry=None,
            answer=None,
            reason=None
        )