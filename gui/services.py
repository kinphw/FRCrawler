from pathlib import Path
from typing import Callable, Optional

import pandas as pd

from gui.settings import DETAIL_TEXT_COLUMNS, PREVIEW_LIST_COLUMNS, RunConfig, build_common_params, get_output_extension


def build_preview_dataframe(past_df, late_df, integ_df) -> pd.DataFrame:
    from harmonizer.main import Harmonizer

    preview_df = Harmonizer(
        past_df=past_df,
        late_df=late_df,
        integ_df=integ_df,
    ).run()

    if preview_df.empty:
        return preview_df

    preview_df = preview_df.copy().reset_index(drop=True)
    if "회신일자" in preview_df.columns:
        preview_df["회신일자"] = pd.to_datetime(preview_df["회신일자"], errors="coerce").dt.strftime("%Y-%m-%d")
        preview_df["회신일자"] = preview_df["회신일자"].fillna("")

    for column in PREVIEW_LIST_COLUMNS + DETAIL_TEXT_COLUMNS:
        if column not in preview_df.columns:
            preview_df[column] = ""
        preview_df[column] = preview_df[column].fillna("").astype(str)

    return preview_df


def collect_result_dataframe(
    config: RunConfig,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> tuple[dict[str, int], list[str], pd.DataFrame]:
    common_params = build_common_params(config)
    counts: dict[str, int] = {}
    notes: list[str] = ["테스트/실행은 건수 확인과 상세 수집을 한 번에 수행합니다."]

    past_df = None
    late_df = None
    integ_df = None

    if config.run_past:
        from past.main import main as past_main

        if progress_callback:
            progress_callback("past 수집 시작")
        past_df = past_main(**common_params)
        counts["past"] = len(past_df)
        if progress_callback:
            progress_callback(f"past 수집 완료: {counts['past']}건")

    if config.run_late:
        from late.main import main as late_main

        if progress_callback:
            progress_callback("late 수집 시작")
        late_df = late_main(**common_params)
        counts["late"] = len(late_df)
        if progress_callback:
            progress_callback(f"late 수집 완료: {counts['late']}건")

    if config.run_integ:
        from integ.main import main as integ_main

        if progress_callback:
            progress_callback("integ 수집 시작")
        integ_df = integ_main(**common_params)
        counts["integ"] = len(integ_df)
        if progress_callback:
            progress_callback(f"integ 수집 완료: {counts['integ']}건")

    preview_df = build_preview_dataframe(past_df, late_df, integ_df)
    if progress_callback:
        progress_callback(f"미리보기 데이터프레임 생성 완료: {len(preview_df)}건")

    return counts, notes, preview_df


def export_result_dataframe(result_df: pd.DataFrame, config: RunConfig) -> Path:
    from exporter.exporter import export_dataframe

    export_dataframe(
        result_df,
        output_dir=config.output_dir,
        export_format=config.export_format,
        output_name=config.output_name,
    )
    return Path(config.output_dir) / f"{config.output_name}{get_output_extension(config.export_format)}"
