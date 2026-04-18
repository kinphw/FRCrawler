import calendar
from datetime import date, datetime
from typing import Optional

import tkinter as tk
from tkinter import ttk


class DatePicker(ttk.LabelFrame):
    def __init__(self, master: tk.Misc, title: str, initial_value: str):
        super().__init__(master, text=title, padding=10)
        self.selected_date = datetime.strptime(initial_value, "%Y-%m-%d").date()
        self.date_var = tk.StringVar(value=self.selected_date.strftime("%Y-%m-%d"))
        self.calendar_window: Optional[tk.Toplevel] = None
        self.calendar_header_var = tk.StringVar()

        self.display_entry = ttk.Entry(self, textvariable=self.date_var, state="readonly", width=18)
        self.display_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.display_entry.bind("<Button-1>", lambda _event: self.open_calendar())

        ttk.Button(self, text="달력", command=self.open_calendar, width=10).grid(row=0, column=1)
        self.columnconfigure(0, weight=1)

    def get_date_string(self) -> str:
        return self.selected_date.strftime("%Y-%m-%d")

    def set_date_string(self, date_string: str) -> None:
        self.selected_date = datetime.strptime(date_string, "%Y-%m-%d").date()
        self.date_var.set(self.selected_date.strftime("%Y-%m-%d"))
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self._render_calendar()

    def open_calendar(self) -> None:
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self.calendar_window.lift()
            self.calendar_window.focus_force()
            return

        self.calendar_window = tk.Toplevel(self)
        self.calendar_window.title("날짜 선택")
        self.calendar_window.resizable(False, False)
        self.calendar_window.transient(self.winfo_toplevel())

        header = ttk.Frame(self.calendar_window, padding=10)
        header.pack(fill=tk.X)
        ttk.Button(header, text="<", width=4, command=lambda: self._move_month(-1)).pack(side=tk.LEFT)
        ttk.Label(header, textvariable=self.calendar_header_var, anchor="center").pack(side=tk.LEFT, expand=True)
        ttk.Button(header, text=">", width=4, command=lambda: self._move_month(1)).pack(side=tk.RIGHT)

        self.calendar_body = ttk.Frame(self.calendar_window, padding=(10, 0, 10, 10))
        self.calendar_body.pack(fill=tk.BOTH, expand=True)

        self._position_calendar()
        self._render_calendar()
        self.calendar_window.protocol("WM_DELETE_WINDOW", self._close_calendar)

    def _position_calendar(self) -> None:
        if self.calendar_window is None:
            return
        self.calendar_window.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        self.calendar_window.geometry(f"+{x}+{y}")

    def _close_calendar(self) -> None:
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self.calendar_window.destroy()
        self.calendar_window = None

    def _move_month(self, delta: int) -> None:
        year = self.selected_date.year
        month = self.selected_date.month + delta
        if month == 0:
            year -= 1
            month = 12
        elif month == 13:
            year += 1
            month = 1
        day = min(self.selected_date.day, calendar.monthrange(year, month)[1])
        self.selected_date = date(year, month, day)
        self.date_var.set(self.selected_date.strftime("%Y-%m-%d"))
        self._render_calendar()

    def _render_calendar(self) -> None:
        if self.calendar_window is None or not self.calendar_window.winfo_exists():
            return

        for child in self.calendar_body.winfo_children():
            child.destroy()

        year = self.selected_date.year
        month = self.selected_date.month
        self.calendar_header_var.set(f"{year}년 {month:02d}월")

        weekday_labels = ["월", "화", "수", "목", "금", "토", "일"]
        for idx, label in enumerate(weekday_labels):
            ttk.Label(self.calendar_body, text=label, anchor="center", width=4).grid(row=0, column=idx, padx=2, pady=2)

        month_rows = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
        for row_idx, week in enumerate(month_rows, start=1):
            for col_idx, day_number in enumerate(week):
                if day_number == 0:
                    ttk.Label(self.calendar_body, text="", width=4).grid(row=row_idx, column=col_idx, padx=2, pady=2)
                    continue

                button = ttk.Button(
                    self.calendar_body,
                    text=f"{day_number:02d}",
                    width=4,
                    command=lambda selected_day=day_number: self._select_day(selected_day),
                )
                if day_number == self.selected_date.day:
                    button.state(["pressed"])
                button.grid(row=row_idx, column=col_idx, padx=2, pady=2)

        footer = ttk.Frame(self.calendar_body)
        footer.grid(row=len(month_rows) + 1, column=0, columnspan=7, sticky="ew", pady=(8, 0))
        ttk.Button(footer, text="오늘", command=self._select_today).pack(side=tk.LEFT)
        ttk.Button(footer, text="닫기", command=self._close_calendar).pack(side=tk.RIGHT)

    def _select_day(self, day_number: int) -> None:
        self.selected_date = date(self.selected_date.year, self.selected_date.month, day_number)
        self.date_var.set(self.selected_date.strftime("%Y-%m-%d"))
        self._close_calendar()

    def _select_today(self) -> None:
        self.selected_date = date.today()
        self.date_var.set(self.selected_date.strftime("%Y-%m-%d"))
        self._render_calendar()
