import logging
import os
import sys

from logstash_async.formatter import LogstashFormatter
from logstash_async.handler import AsynchronousLogstashHandler

from config.docker_helper import is_docker_container


def setup_logger(label_name: str):
    # Logstash configuration
    if not is_docker_container():
        return

    logstash_host = os.getenv("LOGSTASH_HOST", "localhost")
    logstash_port = int(os.getenv("LOGSTASH_PORT", 9600))

    # Configure AsynchronousLogstashHandler
    logstash_handler = AsynchronousLogstashHandler(
        host=logstash_host,
        port=logstash_port,
        database_path=None  # No local database for buffering
    )
    logstash_handler.setFormatter(
        LogstashFormatter(
            extra={"application": label_name}
        )
    )

    # Configure root logger
    logging.basicConfig(level=logging.INFO)  # Set default log level
    logger = logging.getLogger()
    logger.handlers = []  # Clear any existing handlers
    logger.addHandler(logstash_handler)

    # Console handler for local output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)

    return logger


def ensure_logging_flushed():
    # Flush all logging handlers
    logging.shutdown()


__all__ = ["setup_logger", "ensure_logging_flushed"]

# Example usage
if __name__ == "__main__":
    logger = setup_logger("example_app")
    logger.info("This is an informational message.")
    logger.error("This is an error message.")
    ensure_logging_flushed()
