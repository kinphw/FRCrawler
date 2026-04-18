import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

import pandas as pd

from gui.settings import DETAIL_TEXT_COLUMNS, PREVIEW_LIST_COLUMNS


def open_preview_window(root: tk.Misc, preview_df: pd.DataFrame) -> None:
    if preview_df is None or preview_df.empty:
        messagebox.showinfo("미리보기", "표시할 테스트 데이터가 없습니다.", parent=root)
        return

    window = tk.Toplevel(root)
    window.title(f"테스트 미리보기 ({len(preview_df)}건)")
    window.geometry("1500x900")
    window.minsize(1200, 700)

    paned = ttk.Panedwindow(window, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    left_frame = ttk.Frame(paned)
    right_frame = ttk.Frame(paned)
    paned.add(left_frame, weight=3)
    paned.add(right_frame, weight=4)

    tree = ttk.Treeview(left_frame, columns=PREVIEW_LIST_COLUMNS, show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree.column("구분", width=120, anchor="center")
    tree.column("분야", width=140, anchor="w")
    tree.column("제목", width=540, anchor="w")
    tree.column("회신일자", width=110, anchor="center")
    tree.column("일련번호", width=120, anchor="center")

    for column in PREVIEW_LIST_COLUMNS:
        tree.heading(column, text=column)

    tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=tree.yview)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=tree_scroll.set)

    meta_frame = ttk.LabelFrame(right_frame, text="기본 정보")
    meta_frame.pack(fill=tk.X, padx=4, pady=(0, 8))
    meta_text = tk.StringVar(value="행을 선택하면 상세 내용이 표시됩니다.")
    ttk.Label(meta_frame, textvariable=meta_text, justify="left").pack(anchor="w", padx=10, pady=10)

    detail_widgets: dict[str, scrolledtext.ScrolledText] = {}
    for column in DETAIL_TEXT_COLUMNS:
        frame = ttk.LabelFrame(right_frame, text=column)
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Malgun Gothic", 10))
        widget.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        widget.configure(state=tk.DISABLED)
        detail_widgets[column] = widget

    for idx, row in preview_df.iterrows():
        values = [row.get(column, "") for column in PREVIEW_LIST_COLUMNS]
        tree.insert("", tk.END, iid=str(idx), values=values)

    def render_detail(index: int) -> None:
        row = preview_df.iloc[index]
        meta_lines = [
            f"구분: {row.get('구분', '')}",
            f"분야: {row.get('분야', '')}",
            f"제목: {row.get('제목', '')}",
            f"회신일자: {row.get('회신일자', '')}",
            f"일련번호: {row.get('일련번호', '')}",
        ]
        meta_text.set("\n".join(meta_lines))

        for column, widget in detail_widgets.items():
            widget.configure(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", row.get(column, ""))
            widget.configure(state=tk.DISABLED)

    def on_select(_event=None) -> None:
        selection = tree.selection()
        if not selection:
            return
        render_detail(int(selection[0]))

    tree.bind("<<TreeviewSelect>>", on_select)

    first_items = tree.get_children()
    if first_items:
        tree.selection_set(first_items[0])
        tree.focus(first_items[0])
        render_detail(0)
