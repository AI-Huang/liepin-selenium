import logging
import os
from datetime import datetime


def setup_logger(name=None):
    """
    Setup logger with optional name.

    Creates a logger with appropriate handlers. If a name is provided, creates
    a named logger with only console handler. If no name is provided, sets up
    the root logging configuration with both file and console handlers.

    :param name: Logger name. If None, setup root logging with file handler.
    :type name: str or None
    :return: Configured logger instance
    :rtype: logging.Logger
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(processName)s - %(message)s"
    )

    if name:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(console_handler)

        return logger

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"crawler_{timestamp}.log")

    logger = logging.getLogger("liepin_crawler")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
