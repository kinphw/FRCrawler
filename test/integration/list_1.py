import requests
import json

url = "https://better.fsc.go.kr/fsc_new/replyCase/selectReplyCaseTotalReplyList.do"

headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/TotalReplyList.do?stNo=11&muNo=117&muGpNo=75",
    "User-Agent": "Mozilla/5.0"
}

data = {
    # DataTables가 사용하는 기본 파라미터
    "draw": 1,
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

    "order[0][column]": 0,
    "order[0][dir]": "asc",

    "start": 0,
    "length": 10,

    "search[value]": "title",
    "search[regex]": "",
    "searchKeyword": "",
    "searchCondition": "",
    "searchType": ""

    # 질문에서 예시로 추가하신 날짜 범위(없으면 생략 가능)
    # "searchReplyRegDateStart": "2000-01-01",
    # "searchReplyRegDateEnd":   "2025-03-26"
}

response = requests.post(url, headers=headers, data=data)

# 예쁘게 JSON 포맷으로 출력하기
pretty_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
print(pretty_json)