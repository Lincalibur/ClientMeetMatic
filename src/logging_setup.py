import logging
from logging.handlers import RotatingFileHandler

from src.config import get_app_data_dir

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
MAX_LOG_BYTES = 1_000_000
BACKUP_COUNT = 3


def setup_logging(level=logging.INFO):
    """Configures the root logger to write to both the console and a rotating log file
    under %APPDATA%\\ClientMeetMatic\\logs, so a failed unattended run still leaves a
    trace. Returns the log file path."""
    logs_dir = get_app_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "app.log"

    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [file_handler, console_handler]

    return log_file
