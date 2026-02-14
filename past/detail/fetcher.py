"""HTML 콘텐츠 가져오기 담당"""
import requests
from typing import Optional

from ..config import PASTREQ_DETAIL_URL, DEFAULT_HEADERS, ST_NO, MU_NO, ACT_CD
from common.ssl_adapter import get_legacy_session

class DetailFetcher:
    """상세 페이지 HTML 가져오기"""
    
    def __init__(self):
        self.headers = DEFAULT_HEADERS.copy()
        self.session = get_legacy_session()
        
    def get_html(self, pastreq_idx: int) -> str:
        """상세 페이지 HTML 요청"""
        data = {
            "muNo": MU_NO,
            "stNo": ST_NO,
            "pastreqIdx": pastreq_idx, #실제 리스트에서 사용용하는건 이거 하나뿐이다
            "actCd": ACT_CD
        }
        response = self.session.post(PASTREQ_DETAIL_URL, headers=self.headers, data=data)
        return response.text