"""
상세 내용 크롤링 클래스
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
import time
import concurrent.futures
from tqdm import tqdm
import re

from late.models import DetailItem, ListItem, CombinedItem
from late.config import LAWREQ_DETAIL_URL, OPINION_DETAIL_URL, DEFAULT_HEADERS, ST_NO, MU_NO, ACT_CD
from late.utils import html_to_text_preserve_p_br, get_td_html_after_th, random_sleep

class DetailCrawler:
    """금융위원회 회신사례 상세 내용 크롤러"""
    
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
        
    def parse_detail_html(self, html_content: str, idx: int, gubun: str) -> DetailItem:
        """
        상세 내용 HTML을 파싱하여 DetailItem 객체 반환
        
        Args:
            html_content: 상세 페이지 HTML
            idx: 문서 식별자 (디버깅용)
            gubun: 문서 유형 (디버깅용)
            
        Returns:
            DetailItem 객체
        """
        title = None
        registrant = None
        reply_date = None
        inquiry = None
        answer = None
        reason = None
        
        # 다양한 파서를 순차적으로 시도
        for parser in ["html.parser", "lxml", "html5lib"]:
            try:
                # 특수 마크업 제거 시도
                # 'data-hwpjson'과 같은 특수 마크업이 문제를 일으키므로 제거
                cleaned_html = html_content
                if 'data-hwpjson' in html_content:
                    cleaned_html = re.sub(r'data-hwpjson="[^"]*"', '', html_content)
                
                soup = BeautifulSoup(cleaned_html, parser)
                
                # 제목 추출
                title_td = soup.find("td", class_="subject")
                if title_td:
                    title_html = str(title_td)
                    title = html_to_text_preserve_p_br(title_html)
                    break  # 성공적으로 파싱됨
                
            except Exception:
                # 디버그 메시지 삭제하여 진행 바 방해 방지
                continue
        
        if not soup:
            # 실패 항목 기록
            self.failed_items.append((idx, gubun, "HTML 파싱 실패"))
            return DetailItem(
                title="[파싱 오류]",
                registrant=None,
                reply_date=None,
                inquiry=None,
                answer=None,
                reason=None
            )
        
        # 기타 정보 추출 - 다양한 방법 시도
        def get_td_content_after_th(th_text):
            # 방법 1: 정확한 텍스트 매칭
            th_tag = soup.find("th", string=lambda x: x and x.strip() == th_text)
            if th_tag:
                td_tag = th_tag.find_next("td")
                if td_tag:
                    return html_to_text_preserve_p_br(str(td_tag))
            
            # 방법 2: 부분 텍스트 매칭
            th_tag = soup.find("th", string=lambda x: x and th_text in x.strip())
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
                    if th.text.strip() == th_text:
                        td_tag = th.find_next("td")
                        if td_tag:
                            return html_to_text_preserve_p_br(str(td_tag))
            
            # 방법 4: 모든 th 태그 검색
            for th in soup.find_all("th"):
                if th.text.strip() == th_text:
                    td_tag = th.find_next("td")
                    if td_tag:
                        return html_to_text_preserve_p_br(str(td_tag))
            
            return None
        
        # 각 필드 추출
        registrant = get_td_content_after_th("등록자")
        reply_date = get_td_content_after_th("회신일")
        inquiry = get_td_content_after_th("질의요지")
        answer = get_td_content_after_th("회답")
        reason = get_td_content_after_th("이유")
        
        # 이유 필드가 없으면 정규식으로 찾기 시도 (출력 없이)
        if not reason:
            reason_pattern = re.search(r'<th[^>]*>이유</th>\s*<td[^>]*>(.*?)</td>', html_content, re.DOTALL | re.IGNORECASE)
            if reason_pattern:
                reason_html = reason_pattern.group(1)
                reason = html_to_text_preserve_p_br(f"<td>{reason_html}</td>")
                # 카운터만 증가시키고 개별 메시지는 출력하지 않음
                self.regex_found_count += 1
        
        return DetailItem(
            title=title if title else "[제목 파싱 오류]",
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
        self.total_processed += 1
        try:
            html_content = self.get_detail_html(idx, gubun)
            detail_item = self.parse_detail_html(html_content, idx, gubun)
            return detail_item
        except Exception as e:
            # 실패 항목 기록 (터미널 출력 없이)
            self.failed_items.append((idx, gubun, str(e)))
            return None
    
    def process_item(self, list_item: ListItem) -> CombinedItem:
        """단일 항목 처리를 위한 helper 함수 (병렬 처리용)"""
        detail_item = self.get_detail_item(list_item.idx, list_item.gubun)
        combined_item = CombinedItem.from_list_and_detail(list_item, detail_item)
        # 너무 빠른 연속 요청 방지
        time.sleep(self.delay_seconds)
        return combined_item
            
    def process_list_items(self, list_items: List[ListItem]) -> List[CombinedItem]:
        """
        목록 아이템 리스트를 처리하여 상세 내용을 포함한 결합 아이템 리스트 반환
        
        Args:
            list_items: 목록 아이템 리스트
            
        Returns:
            결합된 아이템 리스트
        """
        total_items = len(list_items)
        combined_items = []
        
        # 통계 변수 초기화
        self.regex_found_count = 0
        self.total_processed = 0
        self.failed_items = []
        
        print(f"상세 내용 크롤링 시작: 총 {total_items}개 항목")
        
        # 병렬 처리 구현
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_item, item): item for item in list_items}
            
            # tqdm을 사용한 진행 상황 표시 (깔끔하게 유지)
            with tqdm(total=total_items, desc="상세 크롤링") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    combined_item = future.result()
                    combined_items.append(combined_item)
                    pbar.update(1)
        
        # 크롤링 완료 후 요약 정보 출력
        print(f"상세 내용 크롤링 완료: 총 {len(combined_items)}개 항목")
        
        # 정규식 찾기 결과 통계 출력
        if self.regex_found_count > 0:
            print(f"참고: {self.regex_found_count}개 항목은 정규식을 사용하여 '이유' 필드를 찾았습니다.")
            
        # 실패 항목 요약 출력
        if self.failed_items:
            print(f"경고: {len(self.failed_items)}개 항목에서 문제가 발생했습니다.")
            # 처음 3개만 상세 출력
            for i, (idx, gubun, error) in enumerate(self.failed_items[:3]):
                print(f"  - 실패 항목 #{i+1}: idx={idx}, gubun={gubun}, 오류={error[:100]}")
            if len(self.failed_items) > 3:
                print(f"  - 그 외 {len(self.failed_items)-3}개 항목...")
        
        return combined_items
        
    def get_combined_dataframe(self, list_items: List[ListItem]) -> pd.DataFrame:
        """
        목록 아이템과 상세 내용을 결합한 데이터프레임 반환
        """
        combined_items = self.process_list_items(list_items)
        return pd.DataFrame([vars(item) for item in combined_items])