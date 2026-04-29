"""
Base spider class for all spiders
"""

import random
import time
from abc import ABC, abstractmethod

from ..utils.logger import setup_logger
from .browser import Browser


class BaseSpider(ABC):
    """
    Abstract base class for web spiders

    Usage:
        class MySpider(BaseSpider):
            def __init__(self):
                super().__init__("MySpider")

            def parse(self, response):
                # Parse logic here
                pass

        spider = MySpider()
        spider.run()
    """

    def __init__(self, name):
        """
        Initialize spider

        Args:
            name (str): Spider name
        """
        self.name = name
        self.browser = None
        self.logger = setup_logger(name)
        self.data = []
        self.running = False

    @abstractmethod
    def parse(self, response):
        """
        Parse page content

        Args:
            response: Page source or BeautifulSoup object
        """
        pass

    def start_requests(self):
        """Generate initial requests"""
        pass

    def make_request(self, url):
        """
        Make HTTP request using browser

        Args:
            url (str): URL to fetch

        Returns:
            str: Page source
        """
        if not self.browser:
            self.browser = Browser()

        try:
            self.logger.info(f"Fetching: {url}")
            self.browser.get(url)
            self.random_delay()
            return self.browser.get_page_source()
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {str(e)}")
            raise

    def random_delay(self, min_delay=None, max_delay=None):
        """Add random delay to avoid being blocked"""
        from ..config.settings import settings

        min_d = min_delay or settings.RANDOM_DELAY_RANGE[0]
        max_d = max_delay or settings.RANDOM_DELAY_RANGE[1]
        delay = random.uniform(min_d, max_d)
        self.logger.debug(f"Sleeping for {delay:.2f} seconds")
        time.sleep(delay)

    def save_data(self, item):
        """Save scraped item to data list"""
        self.data.append(item)
        self.logger.debug(f"Saved item: {item.get('title', 'No title')}")

    def export_data(self, filename=None, format_type="json"):
        """
        Export collected data to file

        Args:
            filename (str): Output filename
            format_type (str): 'json' or 'csv'
        """
        from ..utils.data_handler import save_to_csv, save_to_json

        if not self.data:
            self.logger.warning("No data to export")
            return

        if not filename:
            filename = f"{self.name}_{int(time.time())}"

        if format_type == "json":
            save_to_json(self.data, filename)
        elif format_type == "csv":
            save_to_csv(self.data, filename)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        self.logger.info(f"Exported {len(self.data)} items to {filename}.{format_type}")

    def run(self):
        """Main entry point to run spider"""
        self.running = True
        self.logger.info(f"Starting spider: {self.name}")

        try:
            self.browser = Browser()
            self.start_requests()

            while self.running:
                # Main spider loop
                pass

        except Exception as e:
            self.logger.error(f"Spider error: {str(e)}", exc_info=True)
        finally:
            self.stop()

    def stop(self):
        """Stop spider and clean up"""
        self.running = False

        if self.browser:
            self.browser.quit()
            self.logger.info("Browser closed")

        self.logger.info(f"Spider {self.name} stopped")

    def __del__(self):
        """Cleanup on object deletion"""
        if self.browser:
            self.browser.quit()
