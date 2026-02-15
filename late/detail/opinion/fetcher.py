"""
비조치의견서 상세 페이지 요청 클래스
"""

from typing import Optional

from late.detail.base_fetcher import BaseFetcher
from late.config import OPINION_DETAIL_URL, ST_NO, MU_NO, ACT_CD

class OpinionFetcher(BaseFetcher):
    """비조치의견서 상세 페이지 요청 클래스"""
    
    def __init__(self, delay_seconds: float = 0.5, session = None):
        super().__init__(delay_seconds, session)
    
    def _get_url(self) -> str:
        """비조치의견서 요청 URL 반환"""
        return OPINION_DETAIL_URL
        
    def _get_request_params(self, idx: int) -> dict:
        """비조치의견서 요청 파라미터 반환"""
        return {
            "muNo": MU_NO,
            "stNo": ST_NO,
            "opinionIdx": idx,
            "actCd": ACT_CD
        }