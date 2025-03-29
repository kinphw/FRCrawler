# 최근회신사례_목록

import requests
import json
import pandas as pd

url = "https://better.fsc.go.kr/fsc_new/replyCase/selectReplyCasePastReplyList.do"
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReplyList.do?stNo=11&muNo=171&muGpNo=75",
    "User-Agent": "Mozilla/5.0"
}

df_list = []
for i in range(40):
    start_val = i * 1000
    data = {
        "draw": 1,
        "start": start_val,
        "length": 1000,
        "searchReplyRegDateStart": "2000-01-01",
        "searchReplyRegDateEnd": "2025-03-31"
    }
    response = requests.post(url, headers=headers, data=data)
    json_data = response.json()
    df_list.append(pd.DataFrame(json_data["data"]))

final_df = pd.concat(df_list, ignore_index=True)
final_df.iloc[0]
print(final_df)
final_df.to_excel("list_all_late.xlsx", index=False)

