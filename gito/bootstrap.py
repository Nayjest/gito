import logging
import os
from datetime import datetime

import microcore as mc
import typer

from .utils import is_running_in_github_action
from .constants import HOME_ENV_PATH, EXECUTABLE


def setup_logging():
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            dt = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
            message, level_name = record.getMessage(), record.levelname
            if record.levelno == logging.WARNING:
                message = mc.ui.yellow(message)
                level_name = mc.ui.yellow(level_name)
            if record.levelno >= logging.ERROR:
                message = mc.ui.red(message)
                level_name = mc.ui.red(level_name)
            return f"{dt} {level_name}: {message}"

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])


def bootstrap():
    """Bootstrap the application with the environment configuration."""
    setup_logging()
    logging.info("Bootstrapping...")
    try:
        mc.configure(
            DOT_ENV_FILE=HOME_ENV_PATH,
            USE_LOGGING=True,
            EMBEDDING_DB_TYPE=mc.EmbeddingDbType.NONE,
        )
    except mc.LLMConfigError as e:
        msg = str(e)
        if is_running_in_github_action():
            ref = os.getenv("GITHUB_WORKFLOW_REF", "")
            if ref:
                # example value: 'owner/repo/.github/workflows/ai-code-review.yml@refs/pull/1/merge'
                ref = ref.split("@")[0]
                ref = ref.split(".github/workflows/")[-1]
                ref = f" (.github/workflows/{ref})"
            msg += (
                f"\nPlease check your GitHub Action Secrets "
                f"and `env` configuration section of the corresponding workflow step{ref}."
            )
        else:
            msg += (
                f"\nPlease run '{EXECUTABLE} setup' "
                "to configure LLM API access (API keys, model, etc)."
            )
        print(mc.ui.red(msg))
        raise SystemExit(2)
    except Exception as e:
        logging.error(f"Unexpected configuration error: {e}")
        raise SystemExit(3)
    mc.logging.LoggingConfig.STRIP_REQUEST_LINES = [300, 15]


app = typer.Typer(pretty_exceptions_show_locals=False)
