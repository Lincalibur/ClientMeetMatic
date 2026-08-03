import json

from src.config import AppConfig, load_config, save_config


def test_load_config_defaults(monkeypatch, tmp_path):
    monkeypatch.delenv('GOOGLE_MAPS_API_KEY', raising=False)
    monkeypatch.delenv('CLIENT_LIST_FILE', raising=False)
    monkeypatch.chdir(tmp_path)  # no .env here to pick up

    config = load_config(config_file_path=tmp_path / "config.json")

    assert config.api_key is None
    assert config.client_list_file == "Client List/Clients.xlsx"
    assert config.start_hour == 9
    assert config.end_hour == 17


def test_load_config_reads_env(monkeypatch, tmp_path):
    monkeypatch.setenv('GOOGLE_MAPS_API_KEY', 'env-key')
    config = load_config(config_file_path=tmp_path / "config.json")
    assert config.api_key == 'env-key'


def test_load_config_file_overrides_env(monkeypatch, tmp_path):
    monkeypatch.setenv('GOOGLE_MAPS_API_KEY', 'env-key')
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({'api_key': 'file-key'}))

    config = load_config(config_file_path=config_file)

    assert config.api_key == 'file-key'


def test_load_config_explicit_overrides_win_over_file_and_env(monkeypatch, tmp_path):
    monkeypatch.setenv('GOOGLE_MAPS_API_KEY', 'env-key')
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({'api_key': 'file-key'}))

    config = load_config(overrides={'api_key': 'override-key'}, config_file_path=config_file)

    assert config.api_key == 'override-key'


def test_save_config_round_trip(tmp_path):
    config_file = tmp_path / "config.json"
    config = AppConfig(api_key='saved-key', start_hour=10)

    save_config(config, config_file_path=config_file)
    loaded = load_config(config_file_path=config_file)

    assert loaded.api_key == 'saved-key'
    assert loaded.start_hour == 10
