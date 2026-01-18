import os
from dotenv import load_dotenv

#################################
# .env 파일 로드
load_dotenv()

print("공통 인수 지정 (.env 파일에서 로드)")

# 공통매개변수 지정 (일자)
common_params = {
    "start_date": os.getenv("START_DATE"),
    "end_date": os.getenv("END_DATE"),
    "max_workers": 64,  # 적절한 값으로 조정
    "delay": 0.2,       # 적절한 값으로 조정
}

# past 호출해서 크롤링

from past.main import main as past_main
# 파라미터 지정해서 실행
print("\n=== PAST 패키지 크롤링 시작 ===")
past_df = past_main(**common_params)
#pg.show(past_df)

# late 호출해서 크롤링

from late.main import main as late_main
print("\n=== LATE 패키지 크롤링 시작 ===")
late_df = late_main(**common_params)

# pg.show(late_df)

# integ 호출해서 크롤링
from integ.main import main as integ_main
print("\n=== INTEG 패키지 크롤링 시작 ===")
integ_df = integ_main(**common_params)
# pg.show(integ_df)

# 3개의 결과를 1개의 df로 합침
print("\n=== Harmonizing ===")
from harmonizer.main import Harmonizer
df_harmonized = Harmonizer = Harmonizer(
    past_df=past_df, 
    late_df=late_df, 
    integ_df=integ_df
).run()

print("\n=== Exporting ===")

# js로 자동전환
from exporter.exporter import export_dataframe
export_dataframe(df_harmonized, output_dir="data")

print("\n=== 완료 ===")
print("data 폴더에 결과물이 저장되었습니다.")

# data/data_i.js 상태로 최종 산출됨