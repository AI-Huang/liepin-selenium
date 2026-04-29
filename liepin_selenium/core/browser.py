"""
Browser wrapper for Selenium operations with page crawling support
"""

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config.settings import settings


class Browser:
    def __init__(self, browser_type=None, headless=None):
        """
        Initialize browser instance

        :param browser_type: Browser type (Chrome, Firefox, Safari)
        :type browser_type: str
        :param headless: Run browser in headless mode
        :type headless: bool
        """
        self.browser_type = browser_type or settings.BROWSER_TYPE
        self.headless = headless if headless is not None else settings.HEADLESS
        self.driver = None
        self._setup_browser()

    def _setup_browser(self):
        """Setup browser with appropriate options"""
        try:
            if self.browser_type == "Chrome":
                options = Options()

                if self.headless:
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")

                options.add_argument(f"--user-agent={settings.USER_AGENT}")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option(
                    "excludeSwitches", ["enable-automation"]
                )
                options.add_experimental_option("useAutomationExtension", False)

                self.driver = webdriver.Chrome(options=options)

            elif self.browser_type == "Firefox":
                self.driver = webdriver.Firefox()

            elif self.browser_type == "Safari":
                self.driver = webdriver.Safari()

            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")

            self.driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(settings.IMPLICIT_WAIT)

        except Exception as e:
            raise RuntimeError(f"Failed to initialize browser: {str(e)}")

    def get(self, url):
        """Navigate to URL"""
        try:
            self.driver.get(url)
        except WebDriverException as e:
            raise RuntimeError(f"Failed to load page: {str(e)}")

    def wait_for_element(self, by, value, timeout=None):
        """
        Wait for element to be present

        :param by: Selenium By locator (e.g., By.ID, By.XPATH)
        :type by: str
        :param value: Locator value
        :type value: str
        :param timeout: Maximum wait time in seconds
        :type timeout: int
        :return: WebElement if found
        :rtype: WebElement
        """
        timeout = timeout or settings.PAGE_LOAD_TIMEOUT
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            raise RuntimeError(f"Element not found: {by}={value}")

    def wait_for_elements(self, by, value, timeout=None):
        """Wait for elements to be present

        :param by: Selenium By locator
        :type by: str
        :param value: Locator value
        :type value: str
        :param timeout: Maximum wait time in seconds
        :type timeout: int
        :return: List of WebElements
        :rtype: list
        """
        timeout = timeout or settings.PAGE_LOAD_TIMEOUT
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            raise RuntimeError(f"Elements not found: {by}={value}")

    def find_element(self, by, value):
        """Find single element

        :param by: Selenium By locator
        :type by: str
        :param value: Locator value
        :type value: str
        :return: WebElement
        :rtype: WebElement
        """
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        """Find multiple elements

        :param by: Selenium By locator
        :type by: str
        :param value: Locator value
        :type value: str
        :return: List of WebElements
        :rtype: list
        """
        return self.driver.find_elements(by, value)

    def execute_script(self, script, *args):
        """Execute JavaScript

        :param script: JavaScript code to execute
        :type script: str
        :param args: Arguments to pass to the script
        :type args: tuple
        :return: Script return value
        """
        return self.driver.execute_script(script, *args)

    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def take_screenshot(self, filename):
        """Take screenshot and save to file

        :param filename: Output filename
        :type filename: str
        :return: Filepath of the saved screenshot
        :rtype: Path
        """
        filepath = settings.SCREENSHOTS_DIR / filename
        self.driver.save_screenshot(str(filepath))
        return filepath

    def get_page_source(self):
        """Get current page source

        :return: Page HTML source
        :rtype: str
        """
        return self.driver.page_source

    def close(self):
        """Close current window"""
        try:
            self.driver.close()
        except Exception as e:
            pass

    def quit(self):
        """Quit browser and clean up"""
        try:
            self.driver.quit()
        except Exception as e:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def parse(self, callback):
        """Placeholder callback function for page parsing"""
        pass

    def get_page(self, url, callback=None):
        """
        Get page and process with callback function

        :param url: URL to navigate to
        :type url: str
        :param callback: Callback function to process page source
        :type callback: callable
        :return: Page source or error
        :rtype: str or Exception
        """
        try:
            self.driver.get(url)
            if callback:
                callback(self.driver.page_source)
            return self.driver.page_source
        except Exception as error:
            return error

    def follow(self, url, callback=None):
        """
        Follow single URL or list of URLs

        :param url: Single URL string or list of URLs
        :type url: str or list
        :param callback: Callback function for each page
        :type callback: callable
        :return: None or error
        :rtype: None or Exception
        """
        try:
            if isinstance(url, str):
                self.get_page(url, callback)
            elif isinstance(url, list):
                for aurl in url:
                    if isinstance(aurl, str):
                        self.get_page(aurl, callback)
        except Exception as error:
            return error

    def followall(self, urls, callback=None):
        """
        Follow all URLs in a list

        :param urls: List of URLs
        :type urls: list
        :param callback: Callback function for each page
        :type callback: callable
        :return: None or error
        :rtype: None or Exception
        """
        try:
            for url in urls:
                self.get_page(url, callback)
        except Exception as error:
            return error

    def send_keys(self, element, value):
        """
        Send keys to element

        :param element: WebElement to send keys to
        :type element: WebElement
        :param value: Value to send
        :type value: str
        :return: None or error
        :rtype: None or Exception
        """
        try:
            element.send_keys(value)
        except Exception as error:
            print(error)
            print("The element param need a object of element.")
            return error

    def clear_content(self, element):
        """
        Clear element content

        :param element: WebElement to clear
        :type element: WebElement
        :return: None or error
        :rtype: None or Exception
        """
        try:
            element.clear()
        except Exception as error:
            print(error)
            print("The element param need a object of element.")
            return error
