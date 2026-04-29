"""
Data handling utilities for saving scraped data
"""

import csv
import json
from datetime import datetime

from ..config.settings import settings
from .logger import setup_logger


def save_to_json(data, filename):
    """
    Save data to JSON file

    Args:
        data (list/dict): Data to save
        filename (str): Output filename (without extension)
    """
    logger = setup_logger("data_handler")

    filepath = settings.DATA_DIR / f"{filename}.json"

    try:
        with open(filepath, "w", encoding=settings.OUTPUT_ENCODING) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Data saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save JSON: {str(e)}")
        raise


def save_to_csv(data, filename):
    """
    Save data to CSV file

    Args:
        data (list): List of dictionaries to save
        filename (str): Output filename (without extension)
    """
    logger = setup_logger("data_handler")

    filepath = settings.DATA_DIR / f"{filename}.csv"

    if not data:
        logger.warning("No data to save")
        return None

    try:
        # Get all unique keys from dictionaries
        keys = set()
        for item in data:
            if isinstance(item, dict):
                keys.update(item.keys())

        with open(filepath, "w", newline="", encoding=settings.OUTPUT_ENCODING) as f:
            writer = csv.DictWriter(f, fieldnames=list(keys))
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"Data saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save CSV: {str(e)}")
        raise


def generate_filename(prefix="data"):
    """
    Generate timestamped filename

    Args:
        prefix (str): Filename prefix

    Returns:
        str: Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"
