import logging
from logging.handlers import RotatingFileHandler

from config.settings import LOG_DIR, ensure_runtime_directories


ensure_runtime_directories()

LOG_FILE = LOG_DIR / "misra_agent.log"


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


logger = logging.getLogger("MISRA")

logger.setLevel(logging.INFO)

logger.propagate = False


if not logger.handlers:

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    logger.addHandler(file_handler)