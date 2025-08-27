import json
from pathlib import Path


class SettingsManager:
    def __init__(self, filepath: str = None):
        if filepath is None:
            filepath = str(Path.home() / ".yt_dlp_downloader_settings.json")
        self.filepath = filepath
        self.settings = {
            "dark_mode": False,
            "download_path": str(Path.home() / "Downloads"),
        }
        self.load()

    def load(self):
        try:
            with open(self.filepath, "r") as f:
                self.settings.update(json.load(f))
        except Exception:
            pass

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception:
            pass

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
