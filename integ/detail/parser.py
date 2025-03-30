"""HTML 파싱 담당"""
from bs4 import BeautifulSoup
import re
from typing import Optional
from dataclasses import dataclass

from integ.models import DetailItem
from integ.utils import html_to_text_preserve_p_br, clean_text

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
    
    def parse(self, html_content: str, dataIdx: int) -> DetailItem:
        """HTML 파싱하여 DetailItem 반환"""
        self.stats.total_processed += 1
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 과제분류
            category = self._get_td_text(soup, "과제분류")

            # 회신일
            reply_date = self._get_td_text(soup, "회신일")
            
            # 건의내용
            inquiry = self._get_td_text(soup, "건의내용")            

            # 검토의견
            answer_conclusion = self._get_td_text(soup, "검토의견")
            
            # 사유
            answer_content = self._get_td_text(soup, "사유")
            
            # 사유
            plan = self._get_td_text(soup, "향후계획")
            
            
            return DetailItem(
                dataIdx=dataIdx,
                category=category,
                reply_date=reply_date,
                inquiry=inquiry,
                answer_conclusion=answer_conclusion,
                answer_content=answer_content,
                plan=plan,                
            )
            
        except Exception as e:
            self.stats.failed_items.append((dataIdx, str(e)))
            return None
    
    # def _get_td_text(self, soup: BeautifulSoup, th_text: str) -> Optional[str]:
    #     """th 텍스트에 해당하는 td의 텍스트 추출"""
    #     th = soup.find('th', string=lambda x: x and th_text in x)
    #     if th and th.find_next_sibling('td'):
    #         return html_to_text_preserve_p_br(str(th.find_next_sibling('td')))
    #     return None

    def _get_td_text(self, soup: BeautifulSoup, th_text: str) -> Optional[str]:
        """th 텍스트에 해당하는 td의 텍스트 추출"""
        from html import unescape
        
        th = soup.find('th', string=lambda x: x and th_text in x)
        if th and th.find_next_sibling('td'):
            td_content = str(th.find_next_sibling('td'))
            # 1. HTML 엔티티를 먼저 변환 (&gt; -> > 등)
            td_content = unescape(td_content)
            # 2. 그 다음 HTML 태그 처리 및 텍스트 정리
            return html_to_text_preserve_p_br(td_content)
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