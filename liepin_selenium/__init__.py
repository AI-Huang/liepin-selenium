"""
Selenium Spider Framework
A robust web scraping framework built on Selenium
"""

__version__ = "1.0.0"
__author__ = "Spider Team"

from .core.base_spider import BaseSpider
from .core.browser import Browser
from .utils.logger import setup_logger

__all__ = ["Browser", "BaseSpider", "setup_logger"]
