import json
import sys
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox


load_dotenv()


CONFIG_PATH = Path("config") / "last_run.json"
DEFAULT_EXPORT_FORMAT = "pickle"
DEFAULT_MAX_WORKERS = 64
DEFAULT_DELAY = 0.2
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_BATCH_SIZE = 1000


@dataclass
class RunConfig:
    start_date: str
    end_date: str
    export_format: str = DEFAULT_EXPORT_FORMAT
    max_workers: int = DEFAULT_MAX_WORKERS
    delay: float = DEFAULT_DELAY
    run_past: bool = True
    run_late: bool = True
    run_integ: bool = True


def get_default_config() -> RunConfig:
    today = datetime.today().date()
    default_start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    default_end = today.strftime("%Y-%m-%d")
    return RunConfig(start_date=default_start, end_date=default_end)


def load_last_config() -> RunConfig:
    default_config = get_default_config()
    if not CONFIG_PATH.exists():
        return default_config

    try:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return RunConfig(
            start_date=payload.get("start_date", default_config.start_date),
            end_date=payload.get("end_date", default_config.end_date),
            export_format=payload.get("export_format", default_config.export_format),
            max_workers=int(payload.get("max_workers", default_config.max_workers)),
            delay=float(payload.get("delay", default_config.delay)),
            run_past=bool(payload.get("run_past", default_config.run_past)),
            run_late=bool(payload.get("run_late", default_config.run_late)),
            run_integ=bool(payload.get("run_integ", default_config.run_integ)),
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return default_config


def save_last_config(config: RunConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_date(date_text: str) -> bool:
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_run_inputs(
    start_date: str,
    end_date: str,
    max_workers_text: str,
    delay_text: str,
    run_flags: list[bool],
) -> tuple[str | None, int | None, float | None]:
    if not start_date or not end_date:
        return "시작 날짜와 종료 날짜를 모두 입력해주세요.", None, None

    if not validate_date(start_date) or not validate_date(end_date):
        return "날짜 형식은 YYYY-MM-DD 이어야 합니다.", None, None

    if start_date > end_date:
        return "시작 날짜는 종료 날짜보다 늦을 수 없습니다.", None, None

    try:
        max_workers = int(max_workers_text.strip())
        if max_workers <= 0:
            raise ValueError
    except ValueError:
        return "병렬 작업 수는 1 이상의 정수여야 합니다.", None, None

    try:
        delay = float(delay_text.strip())
        if delay < 0:
            raise ValueError
    except ValueError:
        return "요청 지연 시간은 0 이상의 숫자여야 합니다.", None, None

    if not any(run_flags):
        return "최소 1개의 실행 대상을 선택해주세요.", None, None

    return None, max_workers, delay


def get_target_counts(config: RunConfig) -> tuple[dict[str, int], list[str]]:
    return get_target_counts_with_progress(config)


def get_target_counts_with_progress(
    config: RunConfig,
    progress_callback=None,
) -> tuple[dict[str, int], list[str]]:
    counts: dict[str, int] = {}
    notes: list[str] = []

    if config.run_past:
        from past.list_crawler import ListCrawler as PastListCrawler

        crawler = PastListCrawler(batch_size=DEFAULT_BATCH_SIZE)
        counts["past"] = crawler.get_filtered_count(
            start_date=config.start_date,
            end_date=config.end_date,
            progress_callback=progress_callback,
        )
        notes.append("past는 사이트에서 날짜 검색을 지원하지 않아 목록 전체를 조회한 뒤 건수를 계산합니다.")

    if config.run_late:
        from late.list_crawler import ListCrawler as LateListCrawler

        crawler = LateListCrawler(batch_size=DEFAULT_BATCH_SIZE)
        counts["late"] = crawler.get_total_count(
            start_date=config.start_date,
            end_date=config.end_date,
            progress_callback=progress_callback,
        )

    if config.run_integ:
        from integ.list_crawler import ListCrawler as IntegListCrawler

        crawler = IntegListCrawler(batch_size=DEFAULT_BATCH_SIZE)
        counts["integ"] = crawler.get_filtered_count(
            start_date=config.start_date,
            end_date=config.end_date,
            progress_callback=progress_callback,
        )
        notes.append("integ는 사이트 특성상 날짜 필터 확인을 위해 목록 전체를 조회한 뒤 건수를 계산합니다.")

    return counts, notes


def get_run_config_from_gui(initial_config: RunConfig) -> RunConfig | None:
    result: RunConfig | None = None

    root = tk.Tk()
    root.title("FRCrawler Settings")
    root.geometry("620x840")
    root.minsize(620, 840)
    root.resizable(False, False)

    start_var = tk.StringVar(value=initial_config.start_date)
    end_var = tk.StringVar(value=initial_config.end_date)
    export_format_var = tk.StringVar(value=initial_config.export_format)
    max_workers_var = tk.StringVar(value=str(initial_config.max_workers))
    delay_var = tk.StringVar(value=str(initial_config.delay))
    run_past_var = tk.BooleanVar(value=initial_config.run_past)
    run_late_var = tk.BooleanVar(value=initial_config.run_late)
    run_integ_var = tk.BooleanVar(value=initial_config.run_integ)
    test_result_var = tk.StringVar(value="테스트 전입니다.")
    is_testing = False
    progress_lines: list[str] = []

    root.columnconfigure(0, weight=1)

    container = tk.Frame(root, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    tk.Label(container, text="시작 날짜 (YYYY-MM-DD)").pack(anchor="w")
    tk.Entry(container, textvariable=start_var, font=("Malgun Gothic", 11)).pack(fill=tk.X, pady=(6, 14), ipady=5)

    tk.Label(container, text="종료 날짜 (YYYY-MM-DD)").pack(anchor="w")
    tk.Entry(container, textvariable=end_var, font=("Malgun Gothic", 11)).pack(fill=tk.X, pady=(6, 14), ipady=5)

    tk.Label(container, text="출력 형식").pack(anchor="w")
    format_frame = tk.Frame(container)
    format_frame.pack(anchor="w", pady=(6, 14))
    tk.Radiobutton(format_frame, text="Pickle (.pkl)", variable=export_format_var, value="pickle").pack(side=tk.LEFT, padx=(0, 10))
    tk.Radiobutton(format_frame, text="Excel (.xlsx)", variable=export_format_var, value="excel").pack(side=tk.LEFT)

    tk.Label(container, text="병렬 작업 수").pack(anchor="w")
    tk.Entry(container, textvariable=max_workers_var, font=("Malgun Gothic", 11)).pack(fill=tk.X, pady=(6, 14), ipady=5)

    tk.Label(container, text="요청 지연 시간(초)").pack(anchor="w")
    tk.Entry(container, textvariable=delay_var, font=("Malgun Gothic", 11)).pack(fill=tk.X, pady=(6, 14), ipady=5)

    tk.Label(container, text="실행 대상").pack(anchor="w")
    targets_frame = tk.Frame(container)
    targets_frame.pack(anchor="w", pady=(6, 18))
    tk.Checkbutton(targets_frame, text="past", variable=run_past_var).pack(side=tk.LEFT, padx=(0, 10))
    tk.Checkbutton(targets_frame, text="late", variable=run_late_var).pack(side=tk.LEFT, padx=(0, 10))
    tk.Checkbutton(targets_frame, text="integ", variable=run_integ_var).pack(side=tk.LEFT)

    tk.Label(container, text="테스트 결과").pack(anchor="w")
    result_box = tk.Label(
        container,
        textvariable=test_result_var,
        anchor="nw",
        justify="left",
        relief=tk.SOLID,
        bd=1,
        bg="white",
        padx=12,
        pady=10,
        height=8,
    )
    result_box.pack(fill=tk.BOTH, expand=True, pady=(6, 18))

    def build_config_from_form() -> RunConfig | None:
        error_message, max_workers, delay = validate_run_inputs(
            start_var.get().strip(),
            end_var.get().strip(),
            max_workers_var.get(),
            delay_var.get(),
            [run_past_var.get(), run_late_var.get(), run_integ_var.get()],
        )
        if error_message:
            messagebox.showwarning("입력 오류", error_message)
            return None

        return RunConfig(
            start_date=start_var.get().strip(),
            end_date=end_var.get().strip(),
            export_format=export_format_var.get(),
            max_workers=max_workers,
            delay=delay,
            run_past=run_past_var.get(),
            run_late=run_late_var.get(),
            run_integ=run_integ_var.get(),
        )

    def set_controls_state(state: str) -> None:
        run_button.config(state=state)
        test_button.config(state=state)
        close_button.config(state=state)

    def set_progress_message(message: str) -> None:
        progress_lines.append(message)
        if len(progress_lines) > 12:
            del progress_lines[:-12]
        test_result_var.set("\n".join(progress_lines))

    def on_test() -> None:
        nonlocal is_testing
        if is_testing:
            return

        config = build_config_from_form()
        if config is None:
            return

        is_testing = True
        set_controls_state(tk.DISABLED)
        progress_lines.clear()
        set_progress_message("대상 건수를 확인하는 중입니다...")
        set_progress_message("잠시만 기다려주세요.")

        def worker() -> None:
            def progress_callback(message: str) -> None:
                root.after(0, lambda: set_progress_message(message))

            try:
                counts, notes = get_target_counts_with_progress(config, progress_callback=progress_callback)
                total = sum(counts.values())
                lines = [f"조회 기간: {config.start_date} ~ {config.end_date}", ""]
                for key in ("past", "late", "integ"):
                    if key in counts:
                        lines.append(f"- {key}: {counts[key]}건")
                lines.append("")
                lines.append(f"합계: {total}건")
                if notes:
                    lines.append("")
                    lines.extend(f"참고: {note}" for note in notes)
                message = "\n".join(lines)
            except Exception as exc:
                message = f"테스트 중 오류가 발생했습니다.\n{type(exc).__name__}: {exc}"

            def finish() -> None:
                nonlocal is_testing
                test_result_var.set(message)
                set_controls_state(tk.NORMAL)
                is_testing = False

            root.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def on_run() -> None:
        nonlocal result
        config = build_config_from_form()
        if config is None:
            return

        result = config
        root.destroy()

    def on_close() -> None:
        root.destroy()

    buttons = tk.Frame(container)
    buttons.pack(fill=tk.X)
    run_button = tk.Button(buttons, text="RUN", command=on_run, width=12, bg="lightblue")
    run_button.pack(side=tk.LEFT)
    test_button = tk.Button(buttons, text="TEST", command=on_test, width=12)
    test_button.pack(side=tk.LEFT, padx=10)
    close_button = tk.Button(buttons, text="닫기", command=on_close, width=12)
    close_button.pack(side=tk.RIGHT)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
    return result


def build_common_params(config: RunConfig) -> dict:
    return {
        "start_date": config.start_date,
        "end_date": config.end_date,
        "max_workers": config.max_workers,
        "delay": config.delay,
    }


def main() -> int:
    print("공통 인수 지정 (GUI 입력)")

    initial_config = load_last_config()
    config = get_run_config_from_gui(initial_config)
    if config is None:
        print("프로그램이 사용자에 의해 종료되었습니다.")
        return 1

    save_last_config(config)

    print(f"입력된 날짜: {config.start_date} ~ {config.end_date}")
    print(f"선택된 형식: {config.export_format}")
    print(f"병렬 작업 수: {config.max_workers}")
    print(f"요청 지연 시간: {config.delay}")

    common_params = build_common_params(config)

    past_df = None
    late_df = None
    integ_df = None

    if config.run_past:
        from past.main import main as past_main

        print("\n=== PAST 패키지 크롤링 시작 ===")
        past_df = past_main(**common_params)

    if config.run_late:
        from late.main import main as late_main

        print("\n=== LATE 패키지 크롤링 시작 ===")
        late_df = late_main(**common_params)

    if config.run_integ:
        from integ.main import main as integ_main

        print("\n=== INTEG 패키지 크롤링 시작 ===")
        integ_df = integ_main(**common_params)

    print("\n=== Harmonizing ===")
    from harmonizer.main import Harmonizer

    df_harmonized = Harmonizer(
        past_df=past_df,
        late_df=late_df,
        integ_df=integ_df,
    ).run()

    print("\n=== Exporting ===")
    from exporter.exporter import export_dataframe

    export_dataframe(df_harmonized, output_dir=DEFAULT_OUTPUT_DIR, export_format=config.export_format)

    print("\n=== 완료 ===")
    print(f"{DEFAULT_OUTPUT_DIR} 폴더에 결과물이 저장되었습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
