import yaml
from pathlib import Path
from poster.config import Config


def test_load_config(tmp_path):
    config_dir = tmp_path / ".poster"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text(yaml.dump({
        "ebay": {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "refresh_token": "test_token",
            "ru_name": "test_runame",
            "environment": "sandbox",
        },
        "defaults": {
            "condition": "USED_GOOD",
            "category_id": "185099",
            "best_offer": True,
        },
    }))
    config = Config(config_dir=config_dir)
    assert config.get("ebay.client_id") == "test_id"
    assert config.get("ebay.environment") == "sandbox"
    assert config.get("defaults.condition") == "USED_GOOD"


def test_get_missing_key_returns_default(tmp_path):
    config_dir = tmp_path / ".poster"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text(yaml.dump({"ebay": {"client_id": "x"}}))
    config = Config(config_dir=config_dir)
    assert config.get("ebay.missing_key") is None
    assert config.get("ebay.missing_key", "fallback") == "fallback"


def test_save_config(tmp_path):
    config_dir = tmp_path / ".poster"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text(yaml.dump({"ebay": {}}))
    config = Config(config_dir=config_dir)
    config.set("ebay.client_id", "new_id")
    config.save()
    reloaded = Config(config_dir=config_dir)
    assert reloaded.get("ebay.client_id") == "new_id"


def test_config_creates_dir_if_missing(tmp_path):
    config_dir = tmp_path / ".poster"
    config = Config(config_dir=config_dir)
    assert config_dir.exists()


def test_ebay_credentials_property(tmp_path):
    config_dir = tmp_path / ".poster"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text(yaml.dump({
        "ebay": {
            "client_id": "cid",
            "client_secret": "csec",
            "refresh_token": "rtok",
            "ru_name": "runame",
            "environment": "sandbox",
        }
    }))
    config = Config(config_dir=config_dir)
    creds = config.ebay_credentials
    assert creds["client_id"] == "cid"
    assert creds["client_secret"] == "csec"
    assert creds["refresh_token"] == "rtok"
