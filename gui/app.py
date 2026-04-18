import queue
import threading
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from gui.preview import open_preview_window
from gui.runtime import capture_runtime_output
from gui.services import collect_result_dataframe, export_result_dataframe
from gui.settings import (
    APP_HEIGHT,
    APP_WIDTH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_OUTPUT_NAME,
    RunConfig,
    get_output_extension,
    load_last_config,
    normalize_output_name,
    save_last_config,
)
from gui.widgets import DatePicker


class FRCrawlerApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("FRCrawler")
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.minsize(1180, 860)

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.running = False
        self.last_preview_df: Optional[pd.DataFrame] = None
        self.last_preview_signature: Optional[tuple] = None
        self.last_counts: dict[str, int] = {}

        self.initial_config = load_last_config()
        self.summary_var = tk.StringVar(value="preview 데이터가 아직 없습니다.")
        self.output_path_var = tk.StringVar()

        self._build_ui()
        self._load_initial_values()
        self._update_output_path_preview()
        self.root.after(100, self._poll_log_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_paned = ttk.Panedwindow(main_frame, orient=tk.VERTICAL)
        top_paned.pack(fill=tk.BOTH, expand=True)

        settings_frame = ttk.Frame(top_paned, padding=4)
        log_frame = ttk.Frame(top_paned, padding=4)
        top_paned.add(settings_frame, weight=2)
        top_paned.add(log_frame, weight=3)

        date_frame = ttk.Frame(settings_frame)
        date_frame.pack(fill=tk.X, pady=(0, 8))
        self.start_picker = DatePicker(date_frame, "시작 날짜", self.initial_config.start_date)
        self.start_picker.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        self.end_picker = DatePicker(date_frame, "종료 날짜", self.initial_config.end_date)
        self.end_picker.pack(side=tk.LEFT, fill=tk.X, expand=True)

        options_row = ttk.Frame(settings_frame)
        options_row.pack(fill=tk.X, pady=(0, 8))

        format_frame = ttk.LabelFrame(options_row, text="출력 형식", padding=10)
        format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.export_format_var = tk.StringVar(value=self.initial_config.export_format)
        ttk.Radiobutton(format_frame, text="Pickle (.pkl)", variable=self.export_format_var, value="pickle").pack(anchor="w")
        ttk.Radiobutton(format_frame, text="Excel (.xlsx)", variable=self.export_format_var, value="excel").pack(anchor="w")

        runtime_frame = ttk.LabelFrame(options_row, text="실행 옵션", padding=10)
        runtime_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(runtime_frame, text="병렬 작업 수").grid(row=0, column=0, sticky="w")
        self.max_workers_var = tk.StringVar(value=str(self.initial_config.max_workers))
        ttk.Entry(runtime_frame, textvariable=self.max_workers_var, width=12).grid(row=0, column=1, sticky="w", padx=(8, 12))
        ttk.Label(runtime_frame, text="요청 지연 시간(초)").grid(row=0, column=2, sticky="w")
        self.delay_var = tk.StringVar(value=str(self.initial_config.delay))
        ttk.Entry(runtime_frame, textvariable=self.delay_var, width=12).grid(row=0, column=3, sticky="w", padx=(8, 0))

        target_frame = ttk.LabelFrame(settings_frame, text="실행 대상", padding=10)
        target_frame.pack(fill=tk.X, pady=(0, 8))
        self.run_past_var = tk.BooleanVar(value=self.initial_config.run_past)
        self.run_late_var = tk.BooleanVar(value=self.initial_config.run_late)
        self.run_integ_var = tk.BooleanVar(value=self.initial_config.run_integ)
        ttk.Checkbutton(target_frame, text="past", variable=self.run_past_var).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(target_frame, text="late", variable=self.run_late_var).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(target_frame, text="integ", variable=self.run_integ_var).pack(side=tk.LEFT)

        output_frame = ttk.LabelFrame(settings_frame, text="저장 설정", padding=10)
        output_frame.pack(fill=tk.X, pady=(0, 8))
        self.output_dir_var = tk.StringVar(value=self.initial_config.output_dir)
        self.output_name_var = tk.StringVar(value=self.initial_config.output_name)

        ttk.Label(output_frame, text="저장 경로").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_dir_var).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        ttk.Button(output_frame, text="폴더", command=self._browse_directory, width=8).grid(row=0, column=2, sticky="e")
        ttk.Button(output_frame, text="파일 선택", command=self._browse_output_file, width=12).grid(row=0, column=3, sticky="e", padx=(8, 0))

        ttk.Label(output_frame, text="파일명").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(output_frame, textvariable=self.output_name_var).grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=(8, 0))
        ttk.Label(output_frame, text="저장 예정 파일").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Label(output_frame, textvariable=self.output_path_var).grid(row=2, column=1, columnspan=3, sticky="w", pady=(8, 0))
        output_frame.columnconfigure(1, weight=1)

        action_frame = ttk.Frame(settings_frame)
        action_frame.pack(fill=tk.X, pady=(0, 8))
        self.run_button = ttk.Button(action_frame, text="RUN", command=self._start_run)
        self.run_button.pack(side=tk.LEFT)
        self.preview_button = ttk.Button(action_frame, text="PREVIEW", command=self._open_preview, state=tk.DISABLED)
        self.preview_button.pack(side=tk.LEFT, padx=(8, 0))
        self.save_button = ttk.Button(action_frame, text="SAVE", command=self._start_save, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=(8, 0))
        self.close_button = ttk.Button(action_frame, text="닫기", command=self._on_close)
        self.close_button.pack(side=tk.RIGHT)

        summary_frame = ttk.LabelFrame(settings_frame, text="상태", padding=10)
        summary_frame.pack(fill=tk.X)
        ttk.Label(summary_frame, textvariable=self.summary_var, justify="left").pack(anchor="w")

        log_box_frame = ttk.LabelFrame(log_frame, text="실행 로그", padding=8)
        log_box_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(log_box_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

        self.export_format_var.trace_add("write", lambda *_: self._update_output_path_preview())
        self.output_dir_var.trace_add("write", lambda *_: self._update_output_path_preview())
        self.output_name_var.trace_add("write", lambda *_: self._update_output_path_preview())

    def _load_initial_values(self) -> None:
        self._append_log("GUI가 준비되었습니다.")
        self._update_summary_panel()

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _queue_log(self, message: str) -> None:
        self.log_queue.put(message)

    def _poll_log_queue(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self._append_log(message)
        self.root.after(100, self._poll_log_queue)

    def _set_running(self, running: bool) -> None:
        self.running = running
        state = tk.DISABLED if running else tk.NORMAL
        self.run_button.config(state=state)
        self.close_button.config(state=state)
        preview_state = tk.NORMAL if (not running and self.last_preview_df is not None and not self.last_preview_df.empty) else tk.DISABLED
        save_state = tk.NORMAL if (not running and self.last_preview_df is not None and not self.last_preview_df.empty) else tk.DISABLED
        self.preview_button.config(state=preview_state)
        self.save_button.config(state=save_state)

    def _update_summary_panel(self) -> None:
        if self.last_preview_df is None or self.last_preview_df.empty:
            self.summary_var.set("preview 데이터가 아직 없습니다.")
            return

        lines = [f"preview 데이터: {len(self.last_preview_df)}건"]
        for key in ("past", "late", "integ"):
            if key in self.last_counts:
                lines.append(f"- {key}: {self.last_counts[key]}건")

        if self.last_preview_signature is not None:
            start_date, end_date = self.last_preview_signature[0], self.last_preview_signature[1]
            lines.append(f"- 기간: {start_date} ~ {end_date}")

        self.summary_var.set("\n".join(lines))

    def _browse_directory(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_dir_var.get() or str(Path.cwd()))
        if selected:
            self.output_dir_var.set(selected)

    def _browse_output_file(self) -> None:
        extension = get_output_extension(self.export_format_var.get())
        filetypes = [("Excel 파일", "*.xlsx")] if extension == ".xlsx" else [("Pickle 파일", "*.pkl")]
        initialdir = self.output_dir_var.get() or str(Path.cwd())
        initialfile = f"{normalize_output_name(self.output_name_var.get()) or DEFAULT_OUTPUT_NAME}{extension}"
        selected = filedialog.asksaveasfilename(
            title="저장 파일 선택",
            defaultextension=extension,
            filetypes=filetypes,
            initialdir=initialdir,
            initialfile=initialfile,
        )
        if selected:
            selected_path = Path(selected)
            self.output_dir_var.set(str(selected_path.parent))
            self.output_name_var.set(normalize_output_name(selected_path.name))

    def _update_output_path_preview(self) -> None:
        output_name = normalize_output_name(self.output_name_var.get()) or DEFAULT_OUTPUT_NAME
        output_dir = self.output_dir_var.get().strip() or DEFAULT_OUTPUT_DIR
        extension = get_output_extension(self.export_format_var.get())
        output_path = Path(output_dir) / f"{output_name}{extension}"
        self.output_path_var.set(str(output_path))

    def _build_config(self) -> Optional[RunConfig]:
        try:
            start_date = self.start_picker.get_date_string()
            end_date = self.end_picker.get_date_string()
        except ValueError:
            messagebox.showwarning("입력 오류", "날짜 선택값이 올바르지 않습니다.", parent=self.root)
            return None

        if start_date > end_date:
            messagebox.showwarning("입력 오류", "시작 날짜는 종료 날짜보다 늦을 수 없습니다.", parent=self.root)
            return None

        try:
            max_workers = int(self.max_workers_var.get().strip())
            if max_workers <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("입력 오류", "병렬 작업 수는 1 이상의 정수여야 합니다.", parent=self.root)
            return None

        try:
            delay = float(self.delay_var.get().strip())
            if delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("입력 오류", "요청 지연 시간은 0 이상의 숫자여야 합니다.", parent=self.root)
            return None

        if not any([self.run_past_var.get(), self.run_late_var.get(), self.run_integ_var.get()]):
            messagebox.showwarning("입력 오류", "최소 1개의 실행 대상을 선택해주세요.", parent=self.root)
            return None

        output_dir = self.output_dir_var.get().strip()
        output_name = normalize_output_name(self.output_name_var.get())
        if not output_dir:
            messagebox.showwarning("입력 오류", "저장 경로를 입력해주세요.", parent=self.root)
            return None
        if not output_name:
            messagebox.showwarning("입력 오류", "파일명을 입력해주세요.", parent=self.root)
            return None

        return RunConfig(
            start_date=start_date,
            end_date=end_date,
            export_format=self.export_format_var.get(),
            max_workers=max_workers,
            delay=delay,
            run_past=self.run_past_var.get(),
            run_late=self.run_late_var.get(),
            run_integ=self.run_integ_var.get(),
            output_dir=output_dir,
            output_name=output_name,
        )

    def _config_signature(self, config: RunConfig) -> tuple:
        return (
            config.start_date,
            config.end_date,
            config.max_workers,
            config.delay,
            config.run_past,
            config.run_late,
            config.run_integ,
        )

    def _run_worker(self, action_name: str, worker_func: Callable[[RunConfig], None]) -> None:
        if self.running:
            return

        config = self._build_config()
        if config is None:
            return

        save_last_config(config)
        self._set_running(True)
        self._append_log("")
        self._append_log(f"[{action_name}] 시작")

        def background() -> None:
            with capture_runtime_output(self._queue_log):
                try:
                    worker_func(config)
                except Exception as exc:
                    self.root.after(0, lambda: self._finish_run(False, f"{action_name} 실패: {type(exc).__name__}: {exc}"))
                else:
                    self.root.after(0, lambda: self._finish_run(True, f"{action_name} 완료"))

        threading.Thread(target=background, daemon=True).start()

    def _finish_run(self, success: bool, message: str) -> None:
        self._append_log(message)
        self._set_running(False)
        self._update_summary_panel()
        if success:
            self.preview_button.config(state=tk.NORMAL if self.last_preview_df is not None and not self.last_preview_df.empty else tk.DISABLED)
            self.save_button.config(state=tk.NORMAL if self.last_preview_df is not None and not self.last_preview_df.empty else tk.DISABLED)

    def _start_run(self) -> None:
        def worker(config: RunConfig) -> None:
            self._queue_log("결과 수집과 미리보기를 실행합니다.")
            counts, notes, preview_df = collect_result_dataframe(config, progress_callback=self._queue_log)

            total = sum(counts.values())
            summary_lines = [f"조회 기간: {config.start_date} ~ {config.end_date}"]
            for key in ("past", "late", "integ"):
                if key in counts:
                    summary_lines.append(f"- {key}: {counts[key]}건")
            summary_lines.append(f"합계: {total}건")
            summary_lines.append(f"미리보기 데이터: {len(preview_df)}건")
            summary_lines.extend(f"참고: {note}" for note in notes)
            summary = "\n".join(summary_lines)

            def finish_preview() -> None:
                self.last_preview_df = preview_df
                self.last_preview_signature = self._config_signature(config)
                self.last_counts = counts
                self._append_log(summary)
                self._update_summary_panel()
                if not preview_df.empty:
                    self.preview_button.config(state=tk.NORMAL)
                    self.save_button.config(state=tk.NORMAL)
                    open_preview_window(self.root, preview_df)

            self.root.after(0, finish_preview)

        self._run_worker("RUN", worker)

    def _start_save(self) -> None:
        if self.running:
            return

        config = self._build_config()
        if config is None:
            return

        if self.last_preview_df is None or self.last_preview_df.empty:
            messagebox.showinfo("저장", "먼저 RUN을 실행해서 결과 데이터를 준비해주세요.", parent=self.root)
            return

        if self.last_preview_signature != self._config_signature(config):
            answer = messagebox.askyesno(
                "설정 변경 감지",
                "현재 화면 설정이 마지막 실행 결과와 다릅니다.\n현재 preview 데이터를 그대로 저장할까요?",
                parent=self.root,
            )
            if not answer:
                return

        save_last_config(config)
        self._set_running(True)
        self._append_log("")
        self._append_log("[SAVE] 시작")

        def background() -> None:
            with capture_runtime_output(self._queue_log):
                try:
                    saved_path = export_result_dataframe(self.last_preview_df.copy(), config)
                except Exception as exc:
                    self.root.after(0, lambda: self._finish_run(False, f"SAVE 실패: {type(exc).__name__}: {exc}"))
                    return

                summary_lines = [f"저장 완료: {saved_path}"]
                for key, count in self.last_counts.items():
                    summary_lines.append(f"- {key}: {count}건")
                summary_lines.append(f"최종 결과: {len(self.last_preview_df)}건")
                summary = "\n".join(summary_lines)
                self.root.after(0, lambda: self._finish_save(summary))

        threading.Thread(target=background, daemon=True).start()

    def _finish_save(self, summary: str) -> None:
        self._append_log(summary)
        self._finish_run(True, "SAVE 완료")

    def _open_preview(self) -> None:
        if self.last_preview_df is None or self.last_preview_df.empty:
            messagebox.showinfo("미리보기", "먼저 TEST 또는 RUN을 실행해서 데이터를 준비해주세요.", parent=self.root)
            return
        open_preview_window(self.root, self.last_preview_df)

    def _on_close(self) -> None:
        if self.running:
            messagebox.showinfo("실행 중", "현재 작업이 진행 중입니다. 완료 후 닫아주세요.", parent=self.root)
            return
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = FRCrawlerApp()
    app.run()
