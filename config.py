"""
크롤링 설정 값을 저장하는 모듈
"""

# 공통 설정
BASE_URL = "https://better.fsc.go.kr/fsc_new/replyCase"
DEFAULT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReplyList.do?stNo=11&muNo=171&muGpNo=75"
}

# 목록 크롤링 설정
LIST_URL = f"{BASE_URL}/selectReplyCasePastReplyList.do"

# 상세 페이지 크롤링 설정
LAWREQ_DETAIL_URL = f"{BASE_URL}/LawreqDetail.do"
OPINION_DETAIL_URL = f"{BASE_URL}/OpinionDetail.do"

# 공통 파라미터
ST_NO = "11"
MU_NO = "171"
ACT_CD = "R"

# 결과 저장 파일명
OUTPUT_EXCEL = "fsc_crawling_result.xlsx"