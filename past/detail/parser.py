"""HTML 파싱 담당"""
from bs4 import BeautifulSoup
import re
from typing import Optional
from dataclasses import dataclass

from past.models import DetailItem
from common.utils import html_to_text_preserve_p_br

@dataclass
class ParsingStats:
    """파싱 통계"""
    regex_found_count: int = 0
    total_processed: int = 0
    failed_items: list = None
    
    def __post_init__(self):
        self.failed_items = []

class DetailParser:
    """상세 페이지 파싱"""
    
    def __init__(self):
        self.stats = ParsingStats()
    
    def parse(self, html_content: str, pastreq_idx: int) -> DetailItem:
        """HTML 파싱하여 DetailItem 반환"""
        self.stats.total_processed += 1
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 질의요지
            inquiry = self._get_td_text(soup, "질의요지")

            # 사실관계
            fact = self._get_td_text(soup, "법령해석요청의 원인이 되는 사실관계")
            
            # 관련법령
            baseLaw = self._get_td_text(soup, "해석대상 법령 조문 및 관련법령")

            # 회신내용
            answer = self._get_td_text(soup, "회답")
            
            # 이유 (여러 방식으로 시도)
            reason = (
                self._get_td_text(soup, "이유") or
                self._get_reason_by_regex(html_content)
            )
            
            return DetailItem(
                inquiry=inquiry,
                fact=fact,
                baseLaw=baseLaw,
                answer=answer,
                reason=reason                
            )
            
        except Exception as e:
            self.stats.failed_items.append((pastreq_idx, str(e)))
            return None
    
    def _get_td_text(self, soup: BeautifulSoup, th_text: str) -> Optional[str]:
        """th 텍스트에 해당하는 td의 텍스트 추출"""
        th = soup.find('th', string=lambda x: x and th_text in x)
        if th and th.find_next_sibling('td'):
            return html_to_text_preserve_p_br(str(th.find_next_sibling('td')))
        return None
    
    def _get_reason_by_regex(self, html_content: str) -> Optional[str]:
        """정규식을 사용하여 이유 부분 추출 시도"""
        # 특정 패턴의 HTML 구조에서 이유 추출 시도
        patterns = [
            r'<th[^>]*>이유</th>\s*<td[^>]*>(.*?)</td>',
            r'<div[^>]*>이유</div>\s*<div[^>]*>(.*?)</div>',
            r'이유\s*[:：]\s*(.*?)(?=<|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                self.stats.regex_found_count += 1
                return html_to_text_preserve_p_br(match.group(1))
        
        return None