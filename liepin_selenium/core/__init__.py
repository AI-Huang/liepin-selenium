"""
Core module containing browser and spider base classes
"""

from .base_spider import BaseSpider
from .browser import Browser
from .crawler import LiepinCrawler
from .parser import JobParser

__all__ = ["LiepinCrawler", "Browser", "JobParser", "BaseSpider"]
__version__ = "1.0.0"
