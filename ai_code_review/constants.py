from pathlib import Path


PROJECT_CONFIG_FILE = Path(".ai-code-review.toml")
PROJECT_CONFIG_DEFAULTS_FILE = Path(__file__).resolve().parent / PROJECT_CONFIG_FILE
ENV_CONFIG_FILE = Path("~/.env.ai-code-review").expanduser()
JSON_REPORT_FILE_NAME = "code-review-report.json"
