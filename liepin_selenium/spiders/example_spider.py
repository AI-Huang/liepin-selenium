"""
Example spider implementation
"""

from bs4 import BeautifulSoup

from ..core.base_spider import BaseSpider
from ..utils.decorators import retry, timer


class ExampleSpider(BaseSpider):
    """
    Example spider demonstrating the framework usage
    """

    def __init__(self):
        super().__init__("ExampleSpider")
        self.start_urls = []

    def start_requests(self):
        """Generate initial requests"""
        # Add your start URLs here
        self.start_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
        ]

        for url in self.start_urls:
            self.parse_page(url)

    @retry(max_retries=3, delay=2)
    def parse_page(self, url):
        """
        Parse a single page

        Args:
            url (str): URL to parse
        """
        response = self.make_request(url)
        soup = BeautifulSoup(response, "lxml")

        # Extract data using BeautifulSoup
        items = []

        # Example: Find all article titles
        articles = soup.find_all("article")
        for article in articles:
            item = {
                "title": article.find("h2").text.strip() if article.find("h2") else "",
                "url": article.find("a")["href"] if article.find("a") else "",
                "content": article.find("p").text.strip() if article.find("p") else "",
            }
            items.append(item)
            self.save_data(item)

        self.logger.info(f"Parsed {len(items)} items from {url}")

    @timer
    def run(self):
        """Run the spider"""
        super().run()


if __name__ == "__main__":
    spider = ExampleSpider()
    spider.run()
