# 최근회신사례_목록 : 테스트

import requests
import json

url = "https://better.fsc.go.kr/fsc_new/replyCase/selectReplyCasePastReplyList.do"

headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReplyList.do?stNo=11&muNo=171&muGpNo=75",
    "User-Agent": "Mozilla/5.0"
}

data = {
    "draw": 1,
    "start": 0,
    "length": 1,
    "searchReplyRegDateStart": "2000-01-01",
    "searchReplyRegDateEnd": "2025-03-24"
    # 다른 필드들은 빈 값으로 넘겨도 OK
}

response = requests.post(url, headers=headers, data=data)
# 예쁘게 출력
pretty_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
print(pretty_json)
