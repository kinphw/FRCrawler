# 통합 run
# v0.0.2 : 250331

#################################

import tkinter as tk
from tkinter import simpledialog
import sys
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import sys

# 기본값 설정
default_start = "2025-03-25"
default_end = "2025-06-30"

# 날짜 입력을 저장할 변수
start_date = default_start
end_date = default_end
run_clicked = False

def run_gui():
    global start_date, end_date, run_clicked
    
    # Tkinter root 생성
    root = tk.Tk()
    root.title("FRCrawler Date Input")
    root.geometry("300x300")

    # 시작 날짜 라벨 및 입력창
    tk.Label(root, text="시작 날짜 (YYYY-MM-DD):").pack(pady=(20, 5))
    start_entry = tk.Entry(root)
    start_entry.insert(0, default_start)
    start_entry.pack()

    # 종료 날짜 라벨 및 입력창
    tk.Label(root, text="종료 날짜 (YYYY-MM-DD):").pack(pady=(10, 5))
    end_entry = tk.Entry(root)
    end_entry.insert(0, default_end)
    end_entry.pack()

    # 출력 형식 선택 (Radiobutton)
    tk.Label(root, text="출력 형식:").pack(pady=(10, 5))
    export_format_var = tk.StringVar(value="pickle")
    
    frame_format = tk.Frame(root)
    frame_format.pack()
    
    tk.Radiobutton(frame_format, text="Pickle (.pkl)", variable=export_format_var, value="pickle").pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(frame_format, text="Excel (.xlsx)", variable=export_format_var, value="excel").pack(side=tk.LEFT, padx=5)


    def validate_date(date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def on_run():
        global start_date, end_date, run_clicked, selected_format
        start_date = start_entry.get()
        end_date = end_entry.get()
        selected_format = export_format_var.get()
        
        if not start_date or not end_date:
            messagebox.showwarning("입력 오류", "날짜를 모두 입력해주세요.")
            return

        if not validate_date(start_date) or not validate_date(end_date):
            messagebox.showwarning("입력 오류", "날짜 형식이 올바르지 않습니다.\n(YYYY-MM-DD 형식으로 입력해주세요)")
            return

        run_clicked = True
        root.destroy()

    # RUN 버튼
    tk.Button(root, text="RUN", command=on_run, width=10, bg="lightblue").pack(pady=20)

    root.mainloop()

print("공통 인수 지정 (GUI 입력)")

# GUI 실행하여 사용자 입력 받기
selected_format = "pickle" # 기본값
run_gui()

if not run_clicked:
    print("프로그램이 사용자에 의해 종료되었습니다.")
    sys.exit()

print(f"입력된 날짜: {start_date} ~ {end_date}")
print(f"선택된 형식: {selected_format}")

# 공통매개변수 지정 (일자)
common_params = {
    "start_date": start_date,
    "end_date": end_date,
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

# 선택된 형식으로 저장
from exporter.exporter import export_dataframe
export_dataframe(df_harmonized, output_dir="output", export_format=selected_format)

print("\n=== 완료 ===")
print("data 폴더에 결과물이 저장되었습니다.")

# data/data_i.js 상태로 최종 산출됨