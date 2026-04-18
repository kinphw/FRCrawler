import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path


CONFIG_PATH = Path("config") / "last_run.json"
DEFAULT_EXPORT_FORMAT = "pickle"
DEFAULT_MAX_WORKERS = 64
DEFAULT_DELAY = 0.2
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_OUTPUT_NAME = "db_i"
APP_WIDTH = 1280
APP_HEIGHT = 940
PREVIEW_LIST_COLUMNS = ["구분", "분야", "제목", "회신일자", "일련번호"]
DETAIL_TEXT_COLUMNS = ["질의요지", "회답", "이유"]


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
    output_dir: str = DEFAULT_OUTPUT_DIR
    output_name: str = DEFAULT_OUTPUT_NAME


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
            output_dir=payload.get("output_dir", default_config.output_dir),
            output_name=payload.get("output_name", default_config.output_name),
        )
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return default_config


def save_last_config(config: RunConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def normalize_output_name(output_name: str) -> str:
    value = output_name.strip()
    if not value:
        return ""
    path = Path(value)
    if path.suffix.lower() in {".pkl", ".xlsx"}:
        return path.stem
    return value


def get_output_extension(export_format: str) -> str:
    return ".xlsx" if export_format == "excel" else ".pkl"


def build_common_params(config: RunConfig) -> dict:
    return {
        "start_date": config.start_date,
        "end_date": config.end_date,
        "max_workers": config.max_workers,
        "delay": config.delay,
    }
