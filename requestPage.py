import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class Browser(object):
    def __init__(self, browser="Chrome", headless=True):
        try:
            if browser == "Chrome":
                options = Options()
                if headless:
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                options.add_argument(
                    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                self.driver = webdriver.Chrome(options=options)
            elif browser == "Firefox":
                self.driver = webdriver.Firefox()
            else:
                self.driver = webdriver.Safari()
            self.driver.set_page_load_timeout(30)
        except Exception as error:
            print(f"Browser initialization error: {error}")
            raise

    # 虚函数,用于防止回调函数报错
    def parse(self, callback):
        pass

    # 仅用于网页爬取,使用回调函数进行处理
    def get_page(self, url, callback=parse):
        try:
            self.driver.get(url)
            callback(self.driver.page_source)
            return self.driver.page_source
        except Exception as error:
            return error

    def follow(self, url, callback=parse):
        try:
            if type(url) is str:
                self.get_page(url, callback)
            elif type(url) is list:
                for aurl in url:
                    if type(aurl) is str:
                        self.get_page(aurl, callback)
        except Exception as error:

            return error

    def followall(self, urls, callback=parse):
        try:
            for url in urls:
                self.get_page(url, callback)
        except Exception as error:
            return error

    def find_element(self, label, value):
        return self.driver.find_element(label, value)

    def send_keys(self, element, value):
        try:
            element.send_keys(value)
        except Exception as error:
            print(error)
            print("The element param need a object of element.")
            return error

    def clear_content(self, element):
        try:
            element.clear()
        except Exception as error:
            print(error)
            print("The element param need a object of element.")
            return error

    def close(self):
        try:
            self.driver.close()
        except Exception as e:
            print(f"Error closing browser window: {e}")

    def quit(self):
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Error quitting browser: {e}")


def parse(response):
    assert "Python" in browser.driver.title
    elem = browser.driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    # elem.send_keys(Keys.RETURN)
    browser.send_keys(elem, Keys.RETURN)
    assert "No resutls found." not in browser.driver.page_source
    print(type(elem))
    print(elem)
    browser.get_page("https://www.baidu.com/")


if __name__ == "__main__":
    browser = Browser("Firefox")
    browser.get_page("http://www.python.org/", parse)
    browser.close()
