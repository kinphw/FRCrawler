"""
통합회신사례 크롤링 설정 값
"""

# 공통 설정
BASE_URL = "https://better.fsc.go.kr/fsc_new"
DEFAULT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://better.fsc.go.kr",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/TotalReplyList.do?stNo=11&muNo=117&muGpNo=75"
}

# 목록 크롤링 설정
LIST_URL = f"{BASE_URL}/replyCase/selectReplyCaseTotalReplyList.do"

# 상세 페이지 크롤링 설정
LAWREQ_DETAIL_URL = f"{BASE_URL}/replyCase/LawreqDetail.do"
OPINION_DETAIL_URL = f"{BASE_URL}/replyCase/OpinionDetail.do"
EXMNT_DETAIL_URL = f"{BASE_URL}/ExmntTaskDetail.do"

# 공통 파라미터
ST_NO = "11"
MU_NO = "117"
ACT_CD = "R"

# 출력 파일명
OUTPUT_EXCEL = "list_all_integration.xlsx"