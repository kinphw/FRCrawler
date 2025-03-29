"""
상세 페이지 크롤러 팩토리
"""
import logging
import requests

from .base import BaseDetailCrawler
from .lawreq import LawreqDetailCrawler
from .opinion import OpinionDetailCrawler
from .exmnt import ExmntDetailCrawler
from ..config import DEFAULT_HEADERS

logger = logging.getLogger(__name__)

class DetailCrawlerFactory:
    """상세 페이지 크롤러 생성 팩토리"""
    
    def __init__(self):
        """공통 session 초기화"""
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        
    def create_crawler(self, pastreqType: str) -> BaseDetailCrawler:
        """
        구분에 따른 적절한 크롤러 인스턴스 생성
        
        Args:
            pastreqType: 구분 (법령해석/비조치의견서/현장건의과제)
            
        Returns:
            BaseDetailCrawler 구현체
        """
        if "법령해석" in pastreqType:
            return LawreqDetailCrawler(self.session)
        elif "비조치의견서" in pastreqType:
            return OpinionDetailCrawler(self.session)
        elif "현장건의 과제" in pastreqType:
            return ExmntDetailCrawler(self.session)        
        elif "비조치의견서(2014이전)" in pastreqType:
            return ExmntDetailCrawler(self.session)  # 추가필요
        else:
            logger.error(f"알 수 없는 구분: {pastreqType}")
            raise ValueError(f"지원하지 않는 구분입니다: {pastreqType}")

if __name__ == "__main__":
    # 테스트 코드
    factory = DetailCrawlerFactory()
    
    test_cases = ["법령해석", "비조치의견서", "현장건의 과제", "비조치의견서(2014이전)"]
    for case in test_cases:
        try:
            crawler = factory.create_crawler(case)
            print(f"구분: {case}, 생성된 크롤러: {crawler.__class__.__name__}")
        except ValueError as e:
            print(f"오류 발생: {str(e)}")

# function openReplyCasePastReqDetail(idx, gubun){
# 	 if(gubun == 1){ //법령해석
# 		 var url = "/fsc_new/replyCase/LawreqDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), lawreqIdx: idx, actCd: 'R'});
# 	 }else if(gubun == 2){ //비조치의견서
# 		 var url = "/fsc_new/replyCase/OpinionDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), opinionIdx: idx, actCd: 'R'});
# 	 }else if(gubun == 3){ //현장건의 과제
# 		 var url = "/fsc_new/ExmntTaskDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), checkplaceNo: idx, checkplaceSetIdx:"2", actCd: 'R'});
# 	 }else if(gubun == 4){ //과거회신 사례
# 		 var url = "/fsc_new/replyCase/PastReqDetail.do";
# 		 goUrl(url, {muNo:$("#muNo").val(), stNo:$("#stNo").val(), pastreqIdx: idx, actCd: 'R'});
# 	 }
# }            