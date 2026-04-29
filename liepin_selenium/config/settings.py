"""
Configuration settings for selenium_spider
"""

import os
from pathlib import Path


class Settings:
    def __init__(self, keyword="python"):
        # Project paths
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.RAW_DATA_DIR = self.DATA_DIR / "raw"
        self.PROCESSED_DATA_DIR = self.DATA_DIR / "processed"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.SCREENSHOTS_DIR = self.BASE_DIR / "screenshots"

        # Create directories if they don't exist
        for dir_path in [
            self.DATA_DIR,
            self.RAW_DATA_DIR,
            self.PROCESSED_DATA_DIR,
            self.LOGS_DIR,
            self.SCREENSHOTS_DIR,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Browser settings
        self.BROWSER_TYPE = "Chrome"
        self.HEADLESS = True
        self.PAGE_LOAD_TIMEOUT = 30
        self.IMPLICIT_WAIT = 10

        # User agent
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

        # Crawl settings
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        self.RANDOM_DELAY_RANGE = (2, 5)
        self.WAIT_TIME = 5
        self.SCROLL_DELAY = 3

        # Log settings
        self.LOG_LEVEL = "INFO"
        self.LOG_FORMAT = (
            "%(asctime)s - %(name)s - %(levelname)s - %(processName)s - %(message)s"
        )

        # Output settings
        self.OUTPUT_FORMAT = "json"  # csv or json
        self.OUTPUT_ENCODING = "utf-8"
        self.OUTPUT_FILENAME = "liepin_jobs_{keyword}_{timestamp}.json"

        # URL settings
        self.KEYWORD = keyword
        self.URL_TEMPLATE = "https://www.liepin.com/zhaopin/?key={keyword}"
        self.URL = self.URL_TEMPLATE.format(keyword=self.KEYWORD)

        # Headers
        self.HEADERS = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }

        # Parser settings
        self.JOB_CARD_CLASS = "_40108Nrnc3 job-card-pc-container"


# Create singleton settings instance
settings = Settings()
