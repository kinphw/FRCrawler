"""
상세 내용 크롤링 클래스
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
import time

from models import DetailItem, ListItem, CombinedItem
from config import LAWREQ_DETAIL_URL, OPINION_DETAIL_URL, DEFAULT_HEADERS, ST_NO, MU_NO, ACT_CD
from utils import html_to_text_preserve_p_br, get_td_html_after_th, random_sleep

class DetailCrawler:
    """금융위원회 회신사례 상세 내용 크롤러"""
    
    def __init__(self, delay_seconds: float = 1.0):
        """
        Args:
            delay_seconds: 요청 간 지연 시간 (초)
        """
        self.delay_seconds = delay_seconds
        self.headers = DEFAULT_HEADERS.copy()
        
    def get_detail_html(self, idx_value: int, gubun_value: str) -> str:
        """
        상세 내용 HTML을 요청하여 반환
        
        Args:
            idx_value: 상세화면 idx (lawreqIdx/opinionIdx)
            gubun_value: '법령해석' 또는 '비조치의견서' 등
            
        Returns:
            HTML 문자열
        """
        # URL 및 데이터 선택
        if gubun_value == "법령해석":
            url = LAWREQ_DETAIL_URL
            data = {
                "muNo": MU_NO,
                "stNo": ST_NO,
                "lawreqIdx": idx_value,
                "actCd": ACT_CD
            }
        else:
            url = OPINION_DETAIL_URL
            data = {
                "muNo": MU_NO,
                "stNo": ST_NO,
                "opinionIdx": idx_value,
                "actCd": ACT_CD
            }
            
        # 요청 및 응답
        response = requests.post(url, headers=self.headers, data=data)
        return response.text
        
    def parse_detail_html(self, html_content: str) -> DetailItem:
        """
        상세 내용 HTML을 파싱하여 DetailItem 객체 반환
        
        Args:
            html_content: 상세 페이지 HTML
            
        Returns:
            DetailItem 객체
        """
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 제목 추출
        title_td = soup.find("td", class_="subject")
        title_html = str(title_td) if title_td else ""
        title = html_to_text_preserve_p_br(title_html)
        
        # 기타 정보 추출
        registrant_html = get_td_html_after_th(soup, "등록자")
        registrant = html_to_text_preserve_p_br(registrant_html) if registrant_html else None
        
        reply_date_html = get_td_html_after_th(soup, "회신일")
        reply_date = html_to_text_preserve_p_br(reply_date_html) if reply_date_html else None
        
        inquiry_html = get_td_html_after_th(soup, "질의요지")
        inquiry = html_to_text_preserve_p_br(inquiry_html) if inquiry_html else None
        
        answer_html = get_td_html_after_th(soup, "회답")
        answer = html_to_text_preserve_p_br(answer_html) if answer_html else None
        
        reason_html = get_td_html_after_th(soup, "이유")
        reason = html_to_text_preserve_p_br(reason_html) if reason_html else None
        
        return DetailItem(
            title=title,
            registrant=registrant,
            reply_date=reply_date,
            inquiry=inquiry,
            answer=answer,
            reason=reason
        )
        
    def get_detail_item(self, idx: int, gubun: str) -> Optional[DetailItem]:
        """
        idx와 gubun 값으로 상세 내용을 가져와 파싱
        
        Args:
            idx: 문서 식별자
            gubun: 문서 유형 ('법령해석' 또는 '비조치의견서' 등)
            
        Returns:
            DetailItem 객체, 오류 발생 시 None
        """
        try:
            html_content = self.get_detail_html(idx, gubun)
            detail_item = self.parse_detail_html(html_content)
            return detail_item
        except Exception as e:
            print(f"상세 내용 크롤링 오류 (idx={idx}, gubun={gubun}): {str(e)}")
            return None
            
    def process_list_items(self, list_items: List[ListItem], progress_interval: int = 10) -> List[CombinedItem]:
        """
        목록 아이템 리스트를 처리하여 상세 내용을 포함한 결합 아이템 리스트 반환
        
        Args:
            list_items: 목록 아이템 리스트
            progress_interval: 진행 상황 출력 간격
            
        Returns:
            결합된 아이템 리스트
        """
        total_items = len(list_items)
        combined_items = []
        
        print(f"상세 내용 크롤링 시작: 총 {total_items}개 항목")
        
        for i, list_item in enumerate(list_items):
            # 상세 내용 크롤링
            detail_item = self.get_detail_item(list_item.idx, list_item.gubun)
            
            # 결합 아이템 생성
            combined_item = CombinedItem.from_list_and_detail(list_item, detail_item)
            combined_items.append(combined_item)
            
            # 진행 상황 출력
            if (i + 1) % progress_interval == 0 or (i + 1) == total_items:
                print(f"상세 진행: {i + 1}/{total_items} 항목 처리 완료 ({((i + 1) / total_items * 100):.1f}%)")
                
            # 요청 간 지연
            if i < total_items - 1:
                random_sleep()
                
        print(f"상세 내용 크롤링 완료: 총 {len(combined_items)}개 항목")
        return combined_items
        
    def get_combined_dataframe(self, list_items: List[ListItem]) -> pd.DataFrame:
        """
        목록 아이템과 상세 내용을 결합한 데이터프레임 반환
        """
        combined_items = self.process_list_items(list_items)
        return pd.DataFrame([vars(item) for item in combined_items])