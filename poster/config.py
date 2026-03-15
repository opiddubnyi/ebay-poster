from pathlib import Path
import yaml


DEFAULT_CONFIG_DIR = Path.home() / ".poster"


class Config:
    def __init__(self, config_dir: Path = DEFAULT_CONFIG_DIR):
        self._config_dir = config_dir
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self._config_dir / "config.yaml"
        self._data: dict = {}
        if self._config_file.exists():
            with open(self._config_file) as f:
                self._data = yaml.safe_load(f) or {}

    def get(self, dotted_key: str, default=None):
        keys = dotted_key.split(".")
        value = self._data
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value

    def set(self, dotted_key: str, value) -> None:
        keys = dotted_key.split(".")
        target = self._data
        for key in keys[:-1]:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value

    def save(self) -> None:
        with open(self._config_file, "w") as f:
            yaml.dump(self._data, f, default_flow_style=False)

    @property
    def ebay_credentials(self) -> dict:
        return {
            "client_id": self.get("ebay.client_id"),
            "client_secret": self.get("ebay.client_secret"),
            "refresh_token": self.get("ebay.refresh_token"),
            "ru_name": self.get("ebay.ru_name"),
            "environment": self.get("ebay.environment", "sandbox"),
        }
