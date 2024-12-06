import os
import sys

from loguru import logger
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler


def setup_logger(label_name: str):
    # Loki push URL
    loki_url = "http://" + os.getenv("LOKI_URL", "localhost") + ":3100/loki/api/v1/push"

    # Loguru configuration
    logger.remove()  # Remove default logger
    custom_handler = LokiLoggerHandler(
        url=loki_url,
        labels={"application": label_name},
        timeout=10,
        default_formatter=LoguruFormatter()
    )
    logger.configure(handlers=[{"sink": custom_handler, "serialize": True},
                               {"sink": sys.stdout,
                                "format": "<green>{time}</green> <level>{message}</level>"}])


def ensure_logging_flushed():
    logger.info("Flushing logs to Loki before exit")
    logger.remove()  # Ensure all log entries are flushed before exit


__all__ = ["logger", setup_logger, ensure_logging_flushed]

# Example usage
if __name__ == "__main__":
    logger.info("This is an informational message.")
    logger.error("This is an error message.")
