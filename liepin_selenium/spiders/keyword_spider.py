import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from liepin_selenium.config.settings import Settings
from liepin_selenium.core.browser import Browser
from liepin_selenium.core.parser import JobParser
from liepin_selenium.utils.logger import setup_logger


class KeywordSpider:

    def __init__(self, keyword="python"):
        self.settings = Settings(keyword=keyword)
        self.browser = Browser()
        self.data = []
        self.total_jobs_crawled = 0
        self.current_page = 1
        self.total_pages = None
        self.logger = setup_logger(__name__)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = self.settings.OUTPUT_FILENAME.format(
            keyword=self.settings.KEYWORD, timestamp=timestamp
        )
        self.data_filepath = self.settings.DATA_DIR / filename

    def run(self, max_pages=None):
        """
        Run the spider and crawl all pages until no more pages are available.

        :param max_pages: Maximum number of pages to crawl (None means crawl all)
        :type max_pages: int or None
        """
        self.logger.info(f"Starting KeywordSpider for keyword: {self.settings.KEYWORD}")
        wait = WebDriverWait(self.browser.driver, self.settings.WAIT_TIME)

        try:
            self.browser.get(self.settings.URL)
            self.logger.info(f"Page title: {self.browser.driver.title}")

            # Wait for page to load before first iteration
            try:
                wait.until(
                    EC.any_of(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".job-card-wrapper")
                        ),
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".ant-pagination")
                        ),
                    )
                )
                self.logger.debug("Initial page loaded successfully")
            except TimeoutException:
                self.logger.warning("Timeout waiting for initial page load")

            while True:
                # Check if we've reached max pages
                if max_pages is not None and self.current_page > max_pages:
                    break

                # Show progress
                if self.total_pages:
                    self.logger.info(
                        f"Crawling page {self.current_page}/{self.total_pages}"
                    )
                else:
                    self.logger.info(f"Crawling page {self.current_page}")

                # Get total pages from navigation bar on first page
                if self.current_page == 1:
                    self._get_total_pages()
                    if self.total_pages:
                        self.logger.info(f"Total pages found: {self.total_pages}")

                # Scroll to bottom to load all content
                self.browser.scroll_to_bottom()

                # Parse job cards
                html = self.browser.get_page_source()
                job_cards = JobParser.parse(html)

                self.logger.info(
                    f"Found {len(job_cards)} job listings on page {self.current_page}"
                )

                # Extract job info
                for card in job_cards:
                    job_info = JobParser.extract_job_info(card)
                    if job_info:
                        self.data.append(job_info)
                        self.total_jobs_crawled += 1
                        self.logger.debug(
                            f"Job {self.total_jobs_crawled}: {job_info['title']}"
                        )

                # Export data after each page
                self.export_data(format_type="json")

                # Check if there's a next page
                if not self._has_next_page():
                    self.logger.info("No more pages available.")
                    break

                # Go to next page
                if not self._go_to_next_page():
                    self.logger.warning("Failed to go to next page.")
                    break

                self.current_page += 1

                # Shorter wait for page to load after navigation
                short_wait = WebDriverWait(self.browser.driver, 2)
                try:
                    short_wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".job-card-wrapper")
                        )
                    )
                    self.logger.debug("New page content loaded")
                except TimeoutException:
                    self.logger.debug(
                        "Short wait for page content timed out, continuing"
                    )

            self.logger.info("Crawling complete")
            self.logger.info(f"Total jobs crawled: {self.total_jobs_crawled}")

        finally:
            self.browser.quit()

    def _get_total_pages(self):
        """Get total pages from navigation bar with explicit wait"""
        try:
            # Use shorter wait time since page should already be loaded
            wait = WebDriverWait(self.browser.driver, 3)

            # Try getting total pages from pagination items first (faster)
            try:
                # Wait for pagination items to be present
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".ant-pagination li")
                    )
                )

                # Get all pagination items with title attribute containing page numbers
                pagination_items = self.browser.driver.find_elements(
                    By.CSS_SELECTOR, ".ant-pagination li[title]"
                )

                max_page = 0
                for item in pagination_items:
                    title = item.get_attribute("title")
                    if title and title.isdigit():
                        page_num = int(title)
                        if page_num > max_page:
                            max_page = page_num

                if max_page > 0:
                    self.total_pages = max_page
                    self.logger.debug(
                        f"Found total pages by max title: {self.total_pages}"
                    )
                    return
            except (TimeoutException, Exception) as e:
                self.logger.debug(
                    f"Error getting total pages from pagination items: {str(e)}"
                )

            # Try multiple selectors for pagination info
            selectors = [
                ".ant-pagination-total-text",
                ".pagination-info",
                ".page-info",
            ]

            for selector in selectors:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    text = element.text
                    # Extract number from patterns like "共 100 页" or "1/100"
                    import re

                    match = re.search(r"共\s*(\d+)\s*页", text)
                    if not match:
                        match = re.search(r"/(\d+)", text)
                    if not match:
                        match = re.search(r"(\d+)\s*页", text)
                    if match:
                        self.total_pages = int(match.group(1))
                        self.logger.debug(
                            f"Found total pages from selector '{selector}': {self.total_pages}"
                        )
                        return
                except TimeoutException:
                    continue

            # Try getting from URL parameter
            current_url = self.browser.driver.current_url
            import re

            match = re.search(r"currentPage=(\d+)", current_url)
            if match:
                self.logger.debug(f"Current page from URL: {match.group(1)}")

            self.logger.debug("Could not find total pages from navigation bar")

        except Exception as e:
            self.logger.debug(f"Error getting total pages: {str(e)}")

    def _has_next_page(self):
        """Check if next page button exists and is clickable using explicit wait"""
        wait = WebDriverWait(self.browser.driver, 3)
        # Try multiple selectors to find next page button
        selectors = [
            'button[data-selector="page-next"]',
            "button.next-page",
            ".ant-pagination-next",
            "a.next",
            "li.next a",
            ".ant-pagination-next button",
        ]

        for selector in selectors:
            try:
                # Wait for the element to be present
                next_button = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                # Check if the button is disabled via class
                if "disabled" in next_button.get_attribute("class"):
                    continue
                # Check if aria-disabled is true (ant-design pattern)
                aria_disabled = next_button.get_attribute("aria-disabled")
                if aria_disabled and aria_disabled == "true":
                    self.logger.debug("Next page button is aria-disabled")
                    continue
                # Check if button is visible
                if not next_button.is_displayed():
                    # Try to scroll to the button
                    self.browser.driver.execute_script(
                        "arguments[0].scrollIntoView(true);", next_button
                    )
                    # Wait for it to become visible
                    try:
                        wait.until(EC.visibility_of(next_button))
                    except TimeoutException:
                        continue
                self.logger.debug(f"Found next page button with selector: {selector}")
                return True
            except (NoSuchElementException, TimeoutException):
                continue

        # Also check URL for page information
        current_url = self.browser.driver.current_url
        if "curPage=" in current_url:
            import re

            match = re.search(r"curPage=(\d+)", current_url)
            if match:
                current_page_num = int(match.group(1))
                self.logger.debug(f"Current page number from URL: {current_page_num}")
                # Assume there are more pages if current page is low
                if current_page_num < 10:  # Arbitrary limit
                    self.logger.debug("URL suggests there may be more pages")

        self.logger.debug("No next page button found")
        return False

    def _go_to_next_page(self):
        """Navigate to the next page using explicit wait"""
        wait = WebDriverWait(self.browser.driver, 3)
        selectors = [
            'button[data-selector="page-next"]',
            "button.next-page",
            ".ant-pagination-next",
            "a.next",
            "li.next a",
        ]

        for selector in selectors:
            try:
                # Wait for the element to be clickable
                next_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )

                # Try to click the button
                try:
                    next_button.click()
                except ElementClickInterceptedException:
                    # If element is intercepted, try scrolling to it first
                    self.browser.driver.execute_script(
                        "arguments[0].scrollIntoView(true);", next_button
                    )
                    # Wait for element to be clickable again after scroll
                    next_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    next_button.click()

                # Wait for page to navigate (URL to change or new content to load)
                try:
                    wait.until(EC.staleness_of(next_button))
                except TimeoutException:
                    # If staleness check fails, wait for new content
                    self.logger.debug("Waiting for page navigation...")

                self.logger.debug(
                    f"Successfully navigated to next page using selector: {selector}"
                )
                return True
            except (NoSuchElementException, TimeoutException):
                continue

        self.logger.warning("Failed to find next page button")
        return False

    def export_data(self, filepath=None, format_type="json"):
        """Incrementally export data to file and clear data after export"""
        if not self.data:
            self.logger.warning("No data to export")
            return
        if not filepath:
            filepath = self.data_filepath

        if format_type == "json":
            import json

            existing_data = []
            existing_job_ids = set()

            if filepath.exists():
                try:
                    with open(
                        filepath, "r", encoding=self.settings.OUTPUT_ENCODING
                    ) as f:
                        existing_data = json.load(f)
                    # Collect existing job_ids for deduplication
                    existing_job_ids = {
                        job.get("job_id", "")
                        for job in existing_data
                        if job.get("job_id")
                    }
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_data = []

            # Add new data, skipping duplicates based on job_id
            new_jobs_added = 0
            for job in self.data:
                job_id = job.get("job_id", "")
                # Use job_id for deduplication if available, otherwise fall back to url
                if job_id:
                    if job_id not in existing_job_ids:
                        existing_data.append(job)
                        existing_job_ids.add(job_id)
                        new_jobs_added += 1
                    else:
                        self.logger.debug(
                            f"Skipping duplicate job: {job.get('title', '')} (job_id: {job_id})"
                        )
                else:
                    # Fall back to url if job_id is not available
                    job_url = job.get("url", "")
                    if job_url and job_url not in existing_job_ids:
                        existing_data.append(job)
                        existing_job_ids.add(job_url)
                        new_jobs_added += 1

            with open(filepath, "w", encoding=self.settings.OUTPUT_ENCODING) as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            self.logger.info(
                f"Incrementally exported {new_jobs_added} new jobs to {filepath}"
            )
            self.logger.info(f"Total jobs in file: {len(existing_data)}")

        elif format_type == "csv":
            import csv

            file_exists = filepath.exists()
            with open(
                filepath, "a", encoding=self.settings.OUTPUT_ENCODING, newline=""
            ) as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerows(self.data)

            self.logger.info(
                f"Incrementally exported {len(self.data)} jobs to {filepath}"
            )

        self.data = []

    def preview_results(self, limit=10):
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"Top {min(limit, len(self.data))} Job Results:")
        self.logger.info("=" * 60)

        for i, job in enumerate(self.data[:limit], 1):
            self.logger.info(f"\nJob {i}:")
            self.logger.info(f"Title: {job['title']}")
            self.logger.info(f"Location: {job['location']}")
            self.logger.info(f"Salary: {job['salary']}")
            self.logger.info(f"Experience: {job['experience']}")
            self.logger.info(f"Education: {job['education']}")
            self.logger.info(f"URL: {job['url']}")


if __name__ == "__main__":
    spider = KeywordSpider()
    spider.run()
    spider.preview_results()
    spider.export_data()
