"""
통합회신사례 상세 내용 크롤링 클래스
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
import time
import concurrent.futures
from tqdm import tqdm
import re

from integ.models import DetailItem, ListItem, CombinedItem
from integ.config import LAWREQ_DETAIL_URL, OPINION_DETAIL_URL, EXMNT_DETAIL_URL, DEFAULT_HEADERS, ST_NO, MU_NO, ACT_CD
from integ.utils import html_to_text_preserve_p_br, get_td_html_after_th, random_sleep

class DetailCrawler:
    """금융위원회 통합회신사례 상세 내용 크롤러"""
    
    def __init__(self, delay_seconds: float = 0.5, max_workers: int = 5):
        """
        Args:
            delay_seconds: 요청 간 지연 시간 (초)
            max_workers: 병렬 처리 시 최대 worker 수
        """
        self.delay_seconds = delay_seconds
        self.max_workers = max_workers
        self.headers = DEFAULT_HEADERS.copy()
        # 통계 변수 추가
        self.regex_found_count = 0
        self.total_processed = 0
        self.failed_items = []
    
    def get_detail_html(self, idx_value: int, gubun_value: str) -> str:
        """
        상세 내용 HTML을 요청하여 반환
        
        Args:
            idx_value: 상세화면 idx (lawreqIdx/opinionIdx/checkplaceNo)
            gubun_value: '법령해석' 또는 '비조치의견서' 또는 '현장건의과제'
            
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
        elif gubun_value == "비조치의견서":
            url = OPINION_DETAIL_URL
            data = {
                "muNo": MU_NO,
                "stNo": ST_NO,
                "opinionIdx": idx_value,
                "actCd": ACT_CD
            }
        else:  # 현장건의과제
            url = EXMNT_DETAIL_URL
            data = {
                "muNo": MU_NO,
                "stNo": ST_NO,
                "checkplaceNo": idx_value,
                "checkplaceSetIdx": "2",  # 검토완료 상태
                "actCd": ACT_CD
            }
            
        # 요청 및 응답
        response = requests.post(url, headers=self.headers, data=data)
        return response.text
    
    def parse_detail_html(self, html_content: str, idx: int, gubun: str) -> Optional[DetailItem]:
        """
        상세 내용 HTML을 파싱하여 DetailItem 객체 반환
        
        Args:
            html_content: 상세 페이지 HTML
            idx: 문서 식별자 (디버깅용)
            gubun: 문서 유형 ('법령해석' 또는 '비조치의견서' 또는 '현장건의과제')
            
        Returns:
            DetailItem 객체, 파싱 실패 시 None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 공통 필드: 제목
            subject_td = soup.select_one('.subject')
            title = subject_td.text.strip() if subject_td else "제목 없음"
            
            # 구분에 따라 다른 파싱 로직 적용
            if gubun == "법령해석" or gubun == "비조치의견서":
                return self._parse_lawreq_opinion(soup, title, idx, gubun)
            elif gubun == "현장건의과제":
                return self._parse_exmnt_task(soup, title, idx)
            else:
                print(f"알 수 없는 구분: {gubun}, idx: {idx}")
                return None
                
        except Exception as e:
            print(f"파싱 오류 (idx: {idx}, 구분: {gubun}): {str(e)}")
            self.failed_items.append((idx, gubun, str(e)))
            return None
    
    def _parse_lawreq_opinion(self, soup: BeautifulSoup, title: str, idx: int, gubun: str) -> DetailItem:
        """법령해석/비조치의견서 파싱 함수"""
        # 등록자
        registrant_html = get_td_html_after_th(soup, "등록자")
        registrant = html_to_text_preserve_p_br(registrant_html) if registrant_html else None
        
        # 회신일
        reply_date_html = get_td_html_after_th(soup, "회신일")
        reply_date = html_to_text_preserve_p_br(reply_date_html) if reply_date_html else None
        
        # 질의요지
        inquiry_html = get_td_html_after_th(soup, "질의요지")
        inquiry = html_to_text_preserve_p_br(inquiry_html) if inquiry_html else None
        
        # 회답
        answer_html = get_td_html_after_th(soup, "회답")
        answer = html_to_text_preserve_p_br(answer_html) if answer_html else None
        
        # 이유
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
    
    def _parse_exmnt_task(self, soup: BeautifulSoup, title: str, idx: int) -> DetailItem:
        """현장건의과제 파싱 함수"""
        # 소관부서
        department_html = get_td_html_after_th(soup, "소관부서")
        department = html_to_text_preserve_p_br(department_html) if department_html else None
        
        # 과제분류
        category_html = get_td_html_after_th(soup, "과제분류")
        category_detail = html_to_text_preserve_p_br(category_html) if category_html else None
        
        # 회신일
        reply_date_html = get_td_html_after_th(soup, "회신일")
        reply_date = html_to_text_preserve_p_br(reply_date_html) if reply_date_html else None
        
        # 건의내용
        proposal_html = get_td_html_after_th(soup, "건의내용")
        proposal = html_to_text_preserve_p_br(proposal_html) if proposal_html else None
        
        # 검토의견
        review_html = get_td_html_after_th(soup, "검토의견")
        review_opinion = html_to_text_preserve_p_br(review_html) if review_html else None
        
        # 사유
        reason_html = get_td_html_after_th(soup, "사유")
        review_reason = html_to_text_preserve_p_br(reason_html) if reason_html else None
        
        # 향후계획
        plan_html = get_td_html_after_th(soup, "향후계획")
        future_plan = html_to_text_preserve_p_br(plan_html) if plan_html else None
        
        return DetailItem(
            title=title,
            reply_date=reply_date,
            department=department,
            category_detail=category_detail,
            proposal=proposal,
            review_opinion=review_opinion,
            review_reason=review_reason,
            future_plan=future_plan
        )
    
    def process_item(self, item: ListItem) -> Optional[CombinedItem]:
        """
        단일 목록 아이템을 처리하여 상세 정보와 결합
        
        Args:
            item: 목록 아이템 객체
            
        Returns:
            결합된 아이템 객체, 실패 시 None
        """
        try:
            self.total_processed += 1
            
            # 상세 HTML 가져오기
            html = self.get_detail_html(item.idx, item.gubun)
            
            # 상세 내용 파싱
            detail_item = self.parse_detail_html(html, item.idx, item.gubun)
            
            if detail_item:
                # 결합된 아이템 생성
                return CombinedItem.from_list_and_detail(item, detail_item)
            else:
                return CombinedItem.from_list_and_detail(item)
                
        except Exception as e:
            print(f"처리 오류 (idx: {item.idx}, 구분: {item.gubun}): {str(e)}")
            self.failed_items.append((item.idx, item.gubun, str(e)))
            return None
            
        finally:
            # 요청 간 지연
            time.sleep(self.delay_seconds)
    
    def process_items(self, items: List[ListItem], progress_display: bool = True) -> List[CombinedItem]:
        """
        목록 아이템 리스트를 처리하여 상세 정보와 결합
        
        Args:
            items: 목록 아이템 객체 리스트
            progress_display: 진행 상황 표시 여부
            
        Returns:
            결합된 아이템 객체 리스트
        """
        combined_items = []
        self.total_processed = 0
        self.failed_items = []
        
        if self.max_workers > 1:
            # 병렬 처리
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.process_item, item): item for item in items}
                
                if progress_display:
                    futures_iter = tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="상세 정보 크롤링")
                else:
                    futures_iter = concurrent.futures.as_completed(futures)
                    
                for future in futures_iter:
                    result = future.result()
                    if result:
                        combined_items.append(result)
        else:
            # 순차 처리
            if progress_display:
                items_iter = tqdm(items, desc="상세 정보 크롤링")
            else:
                items_iter = items
                
            for item in items_iter:
                result = self.process_item(item)
                if result:
                    combined_items.append(result)
        
        # 결과 요약 출력
        print(f"\n총 처리 항목: {self.total_processed}개")
        print(f"성공 항목: {len(combined_items)}개")
        print(f"실패 항목: {len(self.failed_items)}개")
        
        if self.failed_items:
            print("\n실패 항목 목록:")
            for idx, gubun, error in self.failed_items[:10]:  # 최대 10개만 표시
                print(f"- idx: {idx}, 구분: {gubun}, 오류: {error}")
            
            if len(self.failed_items) > 10:
                print(f"... 외 {len(self.failed_items) - 10}개")
        
        return combined_items
    
    def create_dataframe(self, combined_items: List[CombinedItem]) -> pd.DataFrame:
        """
        결합된 아이템 리스트를 데이터프레임으로 변환
        
        Args:
            combined_items: 결합된 아이템 객체 리스트
            
        Returns:
            pandas DataFrame
        """
        # 아이템이 없는 경우 빈 DataFrame 반환
        if not combined_items:
            return pd.DataFrame()
            
        # 데이터프레임 생성
        df = pd.DataFrame([vars(item) for item in combined_items])
        
        # 열 순서 정리
        columns = [
            # 목록 항목
            'rownumber', 'idx', 'gubun', 'category', 'list_title', 'regDate', 'number',
            # 상세 항목 (공통)
            'detail_title',
            # 법령해석, 비조치의견서 필드
            'registrant', 'reply_date', 'inquiry', 'answer', 'reason',
            # 현장건의과제 필드
            'department', 'category_detail', 'proposal', 'review_opinion', 
            'review_reason', 'future_plan'
        ]
        
        # 실제로 존재하는 열만 선택
        columns = [col for col in columns if col in df.columns]
        
        return df[columns]