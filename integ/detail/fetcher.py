"""HTML 콘텐츠 가져오기 담당"""
import requests
from typing import Optional

from integ.config import DETAIL_URL, DETAIL_HEADERS, ST_NO, MU_NO, ACT_CD, CHECKPLACE_SET_IDX

class DetailFetcher:
    """상세 페이지 HTML 가져오기"""
    
    def __init__(self):
        self.headers = DETAIL_HEADERS.copy()
        
    def get_html(self, checkplaceNo: int) -> str:
        """상세 페이지 HTML 요청"""
        data = {
            "muNo": MU_NO,
            "stNo": ST_NO,
            "checkplaceNo": checkplaceNo, #실제 리스트에서 사용용하는건 이거 하나뿐이다
            "checkplaceSetIdx": CHECKPLACE_SET_IDX,
            "actCd": ACT_CD
        }
        response = requests.post(DETAIL_URL, headers=self.headers, data=data)
        return response.text
    
if __name__ == "__main__":
    fetcher = DetailFetcher()
    html_content = fetcher.get_html(1437784)  # 예시 checkplaceNo
    import clipboard as cb
    cb.copy(html_content)