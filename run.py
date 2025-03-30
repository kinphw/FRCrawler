# 통합 run

# v0.0.1 : 250326

#################################

import pandasgui as pg

# 공통매개변수 지정 (일자)
common_params = {
    "start_date": "2000-01-01",
    "end_date": "2025-03-31",
    "max_workers": 64,  # 적절한 값으로 조정
    "delay": 0.2,       # 적절한 값으로 조정
}

# past 호출해서 크롤링

from past.main import main as past_main
# 파라미터 지정해서 실행
print("\n=== PAST 패키지 크롤링 시작 ===")
past_df = past_main(**common_params)
pg.show(past_df)

# late 호출해서 크롤링

from late.main import main as late_main
print("\n=== LATE 패키지 크롤링 시작 ===")
late_df = late_main(**common_params)

pg.show(late_df)

# integ 호출해서 크롤링


# 3개의 결과를 1개의 df로 합침


# js로 자동전환

# >> data_i.js 상태로 최종 산출됨