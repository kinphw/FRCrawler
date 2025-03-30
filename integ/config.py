"""
통합회신사례 설정 모듈
"""

# 베이스 URL
BASE_URL = "https://better.fsc.go.kr"

# 목록 API URL
LIST_URL = f"{BASE_URL}/fsc_new/replyCase/selectReplyCaseTotalReplyList.do"

# 상세 페이지 URL
DETAIL_URL = f"{BASE_URL}/fsc_new/ExmntTaskDetail.do"

# HTTP 헤더
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/fsc_new/replyCase/TotalReplyList.do"
}


# 상세 페이지 파라미터 설정
ST_NO = "11"

MU_NO = "117"

ACT_CD = "R"

CHECKPLACE_SET_IDX = "2"  # 현장건의과제에만 필요한 추가 파라미터

# 상세 페이지 요청 헤더
DETAIL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/fsc_new/replyCase/TotalReplyList.do?stNo={ST_NO}&muNo={MU_NO}&muGpNo=75",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive"
}

# 기본 API 파라미터
DEFAULT_LIST_PARAMS = {
    "draw": "1",
    "columns[0][data]": "rownumber",
    "columns[0][name]": "",
    "columns[0][searchable]": "true",
    "columns[0][orderable]": "false",
    "columns[0][search][value]": "",
    "columns[0][search][regex]": "false",
    "columns[1][data]": "pastreqType",
    "columns[1][name]": "",
    "columns[1][searchable]": "true", 
    "columns[1][orderable]": "false",
    "columns[1][search][value]": "",
    "columns[1][search][regex]": "false",
    "columns[2][data]": "title",
    "columns[2][name]": "",
    "columns[2][searchable]": "true",
    "columns[2][orderable]": "false",
    "columns[2][search][value]": "",
    "columns[2][search][regex]": "false",
    "columns[3][data]": "replyRegDate",
    "columns[3][name]": "",
    "columns[3][searchable]": "true",
    "columns[3][orderable]": "false",
    "columns[3][search][value]": "",
    "columns[3][search][regex]": "false",
    "order[0][column]": "0",
    "order[0][dir]": "asc",
    "start": "0",
    "length": "10",
    "search[value]": "",
    "search[regex]": "false",
    "searchKeyword": "",
    "searchCondition": "",
    "searchType": ""
}

# 상세 페이지 공통 파라미터
DETAIL_COMMON_PARAMS = {
    "muNo": "117", 
    "stNo": "11",
    "actCd": "R"
}

# 요청 간 지연 시간 (초)
DEFAULT_DELAY = 0.2

# 병렬 처리 설정
DEFAULT_MAX_WORKERS = 64
DEFAULT_BATCH_SIZE = 1000

# 문서 구분 매핑 (pastreqType -> gubun 값)
GUBUN_MAPPING = {
    "법령해석": 1,
    "비조치의견서": 2,
    "현장건의 과제": 3,    # 현장점검의견
    "비조치의견서(2014이전)": 4     # 과거회신사례
}

# 구분 코드 역매핑 (gubun 코드 -> 문자열)
GUBUN_CODE_TO_NAME = {
    1: "법령해석",
    2: "비조치의견서", 
    3: "현장건의 과제",
    4: "비조치의견서(2014이전)"
}

# 이름으로 코드 찾기
GUBUN_NAME_TO_CODE = {v: k for k, v in GUBUN_CODE_TO_NAME.items()}

# 상세 파라미터 키 매핑
DETAIL_PARAM_KEYS = {
    1: "lawreqIdx",
    2: "opinionIdx",
    3: "checkplaceNo",
    4: "pastreqIdx"
}

# 기타 추가 파라미터 (구분별)
ADDITIONAL_PARAMS = {
    3: {"checkplaceSetIdx": "2"}  # 현장건의과제에만 필요한 추가 파라미터
}

# 일자 형식
DATE_FORMAT = "%Y-%m-%d"

