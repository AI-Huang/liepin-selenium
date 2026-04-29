import time
from parser import JobParser

from browser import Browser
from config import MAX_WAIT_TIME, SCROLL_DELAY, URL


class LiepinCrawler:
    def __init__(self):
        self.browser = Browser()
        self.jobs = []

    def crawl(self):
        print("Starting crawler...")
        self.browser.start()

        try:
            self.browser.get(URL)
            print("Page title:", self.browser.driver.title)

            time.sleep(MAX_WAIT_TIME)
            self.browser.scroll_to_bottom()
            time.sleep(SCROLL_DELAY)

            html = self.browser.get_page_source()
            job_cards = JobParser.parse(html)

            print(f"Found {len(job_cards)} job listings")

            for card in job_cards:
                job_info = JobParser.extract_job_info(card)
                if job_info:
                    self.jobs.append(job_info)

        finally:
            self.browser.quit()

    def print_results(self, limit=10):
        print("\n" + "=" * 60)
        print(f"Top {min(limit, len(self.jobs))} Job Results:")
        print("=" * 60)

        for i, job in enumerate(self.jobs[:limit], 1):
            print(f"\nJob {i}:")
            print(f"Title: {job['title']}")
            print(f"Location: {job['location']}")
            print(f"Salary: {job['salary']}")
            print(f"Experience: {job['experience']}")
            print(f"Education: {job['education']}")
            print(f"URL: {job['url']}")


if __name__ == "__main__":
    crawler = LiepinCrawler()
    crawler.crawl()
    crawler.print_results()
