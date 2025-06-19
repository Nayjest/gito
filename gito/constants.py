import os
from pathlib import Path

PROJECT_GITO_FOLDER = ".gito"
PROJECT_CONFIG_FILE_NAME = "config.toml"
PROJECT_CONFIG_FILE_PATH = Path(".gito") / PROJECT_CONFIG_FILE_NAME
PROJECT_CONFIG_BUNDLED_DEFAULTS_FILE = Path(__file__).resolve().parent / PROJECT_CONFIG_FILE_NAME
HOME_ENV_PATH = Path("~/.gito/.env").expanduser()
JSON_REPORT_FILE_NAME = "code-review-report.json"
EXECUTABLE = "gito"
