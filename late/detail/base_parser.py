"""
크롤러 기본 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import re
from bs4 import BeautifulSoup

from common.utils import html_to_text_preserve_p_br

class BaseParser(ABC):
    """
    HTML 파싱 기본 클래스 - 순수 기능 중심
    각 하위 클래스는 해당 문서 유형에 특화된 파싱 로직을 구현해야 함
    """
    
    @abstractmethod
    def parse(self, html_content: str, idx: int, gubun: str) -> Any:
        """
        상세 내용 HTML을 파싱하여 결과 객체 반환
        
        Args:
            html_content: 상세 페이지 HTML
            idx: 문서 식별자 (디버깅용)
            gubun: 문서 유형 (디버깅용)
            
        Returns:
            파싱된 객체, 하위 클래스에서 결정
        """
        pass
    
    def _create_soup(self, html_content: str) -> Optional[BeautifulSoup]:
        """BeautifulSoup 객체 생성 (다양한 파서 시도) - 유틸리티 메서드"""
        # 특수 마크업 제거
        cleaned_html = html_content
        if 'data-hwpjson' in html_content:
            cleaned_html = re.sub(r'data-hwpjson="[^"]*"', '', html_content)
        
        # 여러 파서 시도
        for parser in ["html.parser", "lxml", "html5lib"]:
            try:
                soup = BeautifulSoup(cleaned_html, parser)
                return soup
            except Exception:
                continue
                
        return None
    
    def _extract_field(self, soup: BeautifulSoup, field_name: str) -> Optional[str]:
        """HTML에서 필드 값 추출 - 유틸리티 메서드"""
        # 방법 1: 정확한 텍스트 매칭
        th_tag = soup.find("th", string=lambda x: x and x.strip() == field_name)
        if th_tag:
            td_tag = th_tag.find_next("td")
            if td_tag:
                return html_to_text_preserve_p_br(str(td_tag))
        
        # 방법 2: 부분 텍스트 매칭
        th_tag = soup.find("th", string=lambda x: x and field_name in x.strip())
        if th_tag:
            td_tag = th_tag.find_next("td")
            if td_tag:
                return html_to_text_preserve_p_br(str(td_tag))
        
        # 방법 3: 클래스 기반 검색 (bc-blue, bc-yellow 등)
        for class_name in ["", "bc-blue", "bc-yellow"]:
            attrs = {"scope": "row"}
            if class_name:
                attrs["class"] = class_name
            
            th_tags = soup.find_all("th", attrs=attrs)
            for th in th_tags:
                if th.text.strip() == field_name:
                    td_tag = th.find_next("td")
                    if td_tag:
                        return html_to_text_preserve_p_br(str(td_tag))
        
        # 방법 4: 모든 th 태그 검색
        for th in soup.find_all("th"):
            if th.text.strip() == field_name:
                td_tag = th.find_next("td")
                if td_tag:
                    return html_to_text_preserve_p_br(str(td_tag))
        
        return None
    
    def _extract_field_by_regex(self, html_content: str, field_name: str) -> Optional[str]:
        """정규식으로 필드 값 추출 시도 - 유틸리티 메서드"""
        pattern = re.search(
            f'<th[^>]*>{field_name}</th>\\s*<td[^>]*>(.*?)</td>', 
            html_content, 
            re.DOTALL | re.IGNORECASE
        )
        if pattern:
            field_html = pattern.group(1)
            return html_to_text_preserve_p_br(f"<td>{field_html}</td>")
        return None