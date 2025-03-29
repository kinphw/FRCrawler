# 법령질의회신_목록 (DataFrame 생성)

import requests
import json
import pandas as pd
import time

url = "https://better.fsc.go.kr/fsc_new/replyCase/selectReplyCasePastReqList.do"
headers = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://better.fsc.go.kr",
    "Referer": "https://better.fsc.go.kr/fsc_new/replyCase/PastReqList.do?stNo=11&muNo=172&muGpNo=75",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

# 먼저 총 레코드 수를 확인하여 필요한 페이지 수 계산
initial_data = {
    "draw": 1,
    "start": 0,
    "length": 10,
    "searchReplyRegDateStart": "2000-01-01",
    "searchReplyRegDateEnd": "2025-03-24"
}

initial_response = requests.post(url, headers=headers, data=initial_data)
total_records = initial_response.json().get("recordsTotal", 0)
print(f"총 항목 수: {total_records}")

# 페이지 수 계산 (한 페이지당 100개 항목)
pages_needed = (total_records + 99) // 100  # 올림 나눗셈
print(f"필요한 페이지 수: {pages_needed}")

# 데이터프레임 목록 생성
df_list = []

# 각 페이지 크롤링
for i in range(pages_needed):
    start_val = i * 100
    data = {
        "draw": i + 1,
        "start": start_val,
        "length": 100,
        "searchReplyRegDateStart": "2000-01-01",
        "searchReplyRegDateEnd": "2025-03-24"
    }
    
    print(f"페이지 {i+1}/{pages_needed} 가져오는 중... (시작 인덱스: {start_val})")
    
    try:
        response = requests.post(url, headers=headers, data=data)
        json_data = response.json()
        
        # 응답에 데이터가 있는지 확인
        if "data" in json_data and json_data["data"]:
            page_df = pd.DataFrame(json_data["data"])
            df_list.append(page_df)
            print(f"  → {len(page_df)}개 항목 추가됨")
        else:
            print(f"  → 데이터 없음")
            
        # 서버 부하 방지를 위한 약간의 지연
        time.sleep(0.5)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        continue

# 모든 데이터프레임 병합
if df_list:
    final_df = pd.concat(df_list, ignore_index=True)
    
    # 결과 정보 표시
    print("\n=== 수집 결과 ===")
    print(f"총 {len(final_df)}개 항목 수집 완료")
    print("\n데이터프레임 정보:")
    print(final_df.info())
    
    print("\n처음 5개 항목:")
    print(final_df.head())
    
    # 컬럼명 출력
    print("\n컬럼명:")
    for col in final_df.columns:
        print(f"  - {col}")
    
    # 중복 항목 확인
    duplicates = final_df.duplicated(subset=["pastreqIdx"]).sum()
    if duplicates > 0:
        print(f"\n주의: {duplicates}개의 중복 항목이 있습니다.")
    
    # CSV로 저장 (선택사항)
    # output_file = "법령질의회신_목록.csv"
    # final_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    # print(f"\n결과가 {output_file}로 저장되었습니다.")
else:
    print("수집된 데이터가 없습니다.")

final_df.head(1)
final_df.to_excel("list_all_past.xlsx", index=False)