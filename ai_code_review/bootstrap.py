import logging
from datetime import datetime

import microcore as mc

from .constants import ENV_CONFIG_FILE


def setup_logging():
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            dt = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
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
    setup_logging()
    logging.info("Bootstrapping...")
    mc.configure(
        DOT_ENV_FILE=ENV_CONFIG_FILE,
        VALIDATE_CONFIG=False,
        USE_LOGGING=True,
        EMBEDDING_DB_TYPE=mc.EmbeddingDbType.NONE,
    )
    mc.logging.LoggingConfig.STRIP_REQUEST_LINES = [350, 15]
