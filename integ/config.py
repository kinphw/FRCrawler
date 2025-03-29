"""
금융위원회 통합회신사례 크롤링 설정 값
v0.0.1 : 250326
"""

# 공통 설정
BASE_URL = "https://better.fsc.go.kr"
LIST_URL = f"{BASE_URL}/fsc_new/replyCase/selectReplyCaseTotalReplyList.do"
DETAIL_URL = f"{BASE_URL}/fsc_new/replyCase/selectReplyCaseDetail.do"

DEFAULT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReplyList.do",
    "User-Agent": "Mozilla/5.0"
}

# 결과 저장 파일명
OUTPUT_EXCEL = "fsc_integration_crawling_result.xlsx"


