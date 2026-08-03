import json
import os
from dataclasses import dataclass, fields
from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "ClientMeetMatic"

DEFAULT_CLIENT_LIST_FILE = "Client List/Clients.xlsx"
DEFAULT_MEETING_DURATION_MINUTES = 60
DEFAULT_START_HOUR = 9
DEFAULT_END_HOUR = 17
DEFAULT_LUNCH_START_HOUR = 12
DEFAULT_LUNCH_END_HOUR = 13


@dataclass
class AppConfig:
    api_key: str = None
    client_list_file: str = DEFAULT_CLIENT_LIST_FILE
    meeting_duration_minutes: int = DEFAULT_MEETING_DURATION_MINUTES
    start_hour: int = DEFAULT_START_HOUR
    end_hour: int = DEFAULT_END_HOUR
    lunch_start_hour: int = DEFAULT_LUNCH_START_HOUR
    lunch_end_hour: int = DEFAULT_LUNCH_END_HOUR


def get_app_data_dir():
    """%APPDATA%\\ClientMeetMatic — where the packaged .exe keeps config/logs, since it
    can't rely on a .env sitting next to code it doesn't ship as a visible file."""
    base = os.getenv('APPDATA') or str(Path.home())
    app_dir = Path(base) / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_file_path():
    return get_app_data_dir() / "config.json"


def load_config(overrides=None, config_file_path=None):
    """Resolves settings in order: explicit `overrides` (e.g. CLI flags) > the per-user
    config file > `.env`/environment variables (kept for the developer workflow) >
    built-in defaults."""
    load_dotenv()

    config = AppConfig(
        api_key=os.getenv('GOOGLE_MAPS_API_KEY'),
        client_list_file=os.getenv('CLIENT_LIST_FILE', DEFAULT_CLIENT_LIST_FILE),
    )

    config_file_path = config_file_path or get_config_file_path()
    if config_file_path.exists():
        with open(config_file_path, 'r', encoding='utf-8') as f:
            _apply(config, json.load(f))

    if overrides:
        _apply(config, overrides)

    return config


def save_config(config, config_file_path=None):
    config_file_path = config_file_path or get_config_file_path()
    config_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(config.__dict__, f, indent=2)


def _apply(config, values):
    valid_fields = {f.name for f in fields(config)}
    for key, value in values.items():
        if key in valid_fields and value is not None:
            setattr(config, key, value)
