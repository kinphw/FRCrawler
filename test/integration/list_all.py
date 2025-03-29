# list_all.py
import requests
import json
import pandas as pd
from tqdm import tqdm

url = "https://better.fsc.go.kr/fsc_new/replyCase/selectReplyCaseTotalReplyList.do"

headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReplyList.do?stNo=11&muNo=117&muGpNo=75",
    "User-Agent": "Mozilla/5.0"
}

# ------------------------------------------------------------------------------
# (1) 먼저 length=1 정도로 요청하여 recordsTotal(총 데이터 건수)을 가져온다.
# ------------------------------------------------------------------------------
initial_data = {
    "draw": 1,

    # DataTables 파라미터 (columns, search 등)
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
    "length": 1,          # 1건만 요청해서 전체 개수를 알아낼 목적

    "search[value]": "",
    "search[regex]": "false",
    "searchKeyword": "",
    "searchCondition": "",
    "searchType": ""
}

response = requests.post(url, headers=headers, data=initial_data)
json_data = response.json()

# 전체 레코드 수 가져오기
total_records = json_data.get("recordsTotal", 0)
print("총 레코드 수:", total_records)

# ------------------------------------------------------------------------------
# (2) total_records를 기준으로 페이지네이션 반복하여 모든 데이터 수집
# ------------------------------------------------------------------------------
page_size = 1000  # 페이지당 100건씩 가져오도록 설정
df_list = []

for start_val in tqdm(range(0, total_records, page_size), total=total_records//page_size + 1):
    data = {
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

        "start": start_val,
        "length": page_size,

        "search[value]": "",
        "search[regex]": "false",
        "searchKeyword": "",
        "searchCondition": "",
        "searchType": ""
    }

    response = requests.post(url, headers=headers, data=data)
    json_data = response.json()

    # 혹시 결과가 비거나 서버 에러가 있으면 중단 처리
    if "data" not in json_data or not json_data["data"]:
        print("No more data or 'data' key missing at start:", start_val)
        break

    # 페이지 데이터 -> DataFrame
    df_page = pd.DataFrame(json_data["data"])
    df_list.append(df_page)

# ------------------------------------------------------------------------------
# (3) 모든 페이지를 합쳐 최종 DataFrame으로 만들기
# ------------------------------------------------------------------------------
final_df = pd.concat(df_list, ignore_index=True)
print(final_df)
print("\n수집된 건수:", len(final_df))

final_df.to_pickle("list_all_integration.pkl")
final_df.to_excel("list_all_integration.xlsx", index=False)