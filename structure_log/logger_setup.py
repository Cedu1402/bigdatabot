import os
import sys

from loguru import logger
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler

# Loki push URL
LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100/loki/api/v1/push")

# Loguru configuration
logger.remove()  # Remove default logger
custom_handler = LokiLoggerHandler(
    url=LOKI_URL,
    labels={"application": "solana-bot"},
    timeout=10,
    default_formatter=LoguruFormatter()
)

logger.configure(handlers=[{"sink": custom_handler, "serialize": True},
                           {"sink": sys.stdout,
                            "format": "<green>{time}</green> <level>{message}</level>"}])

__all__ = ["logger"]

# Example usage
if __name__ == "__main__":
    logger.info("This is an informational message.")
    logger.error("This is an error message.")
