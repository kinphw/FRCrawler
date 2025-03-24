"""
과거 회신사례(2014년 이전) 크롤링 설정 값
"""

# 공통 설정
BASE_URL = "https://better.fsc.go.kr/fsc_new/replyCase"
DEFAULT_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReqList.do?stNo=11&muNo=172&muGpNo=75"
}

# 목록 크롤링 설정
LIST_URL = f"{BASE_URL}/selectReplyCasePastReqList.do"

# 상세 페이지 크롤링 설정
PASTREQ_DETAIL_URL = f"{BASE_URL}/PastReqDetail.do"

# 공통 파라미터
ST_NO = "11"
MU_NO = "172"  # 과거 법령해석 질의회신 메뉴 번호 (muNo=172)
ACT_CD = "R"

# 결과 저장 파일명
OUTPUT_EXCEL = "fsc_past_crawling_result.xlsx"