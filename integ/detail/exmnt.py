"""
현장건의과제 상세 페이지 크롤러
"""
import logging
from bs4 import BeautifulSoup

from .base import BaseDetailCrawler
from ..models import DetailItem
from ..utils import get_td_html_after_th, html_to_text_preserve_p_br

logger = logging.getLogger(__name__)

class ExmntDetailCrawler(BaseDetailCrawler):
    """현장건의과제 상세 페이지 크롤러"""
    
    def parse(self, soup: BeautifulSoup, title: str, idx: int) -> DetailItem:
        """현장건의과제 상세 페이지 파싱"""
        try:
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
                department=department,
                category_detail=category_detail,
                reply_date=reply_date,
                proposal=proposal,
                review_opinion=review_opinion,
                review_reason=review_reason,
                future_plan=future_plan
            )
            
        except Exception as e:
            logger.error(f"현장건의과제 상세 페이지 파싱 실패 (idx: {idx}): {str(e)}")
            return None

if __name__ == "__main__":
    import requests
    from ..config import DEFAULT_HEADERS
    
    # 테스트 코드
    def test_parse():
        crawler = ExmntDetailCrawler(requests.Session())
        # 테스트용 idx (실제 존재하는 현장건의과제 번호로 변경 필요)
        test_idx = "12345"
        params = {"idx": test_idx}
        
        try:
            response = crawler.session.post(crawler.DETAIL_URL, data=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            result = crawler.parse(soup, "테스트 제목", test_idx)
            
            print("파싱 결과:")
            for key, value in vars(result).items():
                print(f"{key}: {value}")
                
        except Exception as e:
            print(f"테스트 실패: {str(e)}")
    
    test_parse()