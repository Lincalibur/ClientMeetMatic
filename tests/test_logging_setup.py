import logging

from src.logging_setup import setup_logging


def test_setup_logging_writes_to_file(monkeypatch, tmp_path):
    monkeypatch.setenv('APPDATA', str(tmp_path))

    log_file = setup_logging()
    logging.getLogger("test_logging_setup").info("hello from the test")
    for handler in logging.getLogger().handlers:
        handler.flush()

    assert log_file.exists()
    assert "hello from the test" in log_file.read_text(encoding='utf-8')

    for handler in list(logging.getLogger().handlers):
        handler.close()
        logging.getLogger().removeHandler(handler)
