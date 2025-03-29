# 법령질의회신_목록 : 테스트

import requests
import json

url = "https://better.fsc.go.kr/fsc_new/replyCase/selectReplyCasePastReqList.do"

headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReqList.do?stNo=11&muNo=172&muGpNo=75",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

data = {
    "draw": 1,
    "start": 0,
    "length": 10,  # 10개 항목 가져오기
    "searchReplyRegDateStart": "2000-01-01",
    "searchReplyRegDateEnd": "2025-03-24"
    # 다른 필드들은 빈 값으로 넘겨도 OK
}

response = requests.post(url, headers=headers, data=data)

# 상태 코드 확인
print(f"상태 코드: {response.status_code}")

# 예쁘게 출력
try:
    pretty_json = json.dumps(response.json(), indent=2, ensure_ascii=False)
    print(pretty_json)
    
    # 총 항목 수 출력
    total_records = response.json().get("recordsTotal", 0)
    print(f"\n총 항목 수: {total_records}")
    
    # 첫 번째 항목 정보 출력
    if response.json().get("data"):
        first_item = response.json()["data"][0]
        print("\n첫 번째 항목 정보:")
        for key, value in first_item.items():
            print(f"  {key}: {value}")
except Exception as e:
    print(f"JSON 파싱 오류: {e}")
    print("응답 내용:")
    print(response.text[:500])  # 처음 500자만 출력