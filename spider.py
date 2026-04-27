import os
import random
import threading
import time

from bs4 import BeautifulSoup

import acquire
import requestPage
from logger import logger

x_lock = threading.Lock()
y_lock = threading.Lock()

detailpageurls = []
spidersingle = True


class listpage(requestPage.Browser):

    def __init__(self, browser="Chrome"):
        super().__init__(browser)
        self.page_count = 0

    def start_url(self, starturl):
        logger.info(f"开始爬取列表页: {starturl}")
        self.get_page(starturl, self.parse)

    def parse(self, response):
        try:
            soup = BeautifulSoup(response, "lxml")
            joblist = soup.find("div", "main").find("ul", "super-jobs job-lists")

            if joblist:
                urls = joblist.find_all("a", "ellipsis")[::2]
                with acquire.acquire(x_lock, y_lock):
                    detailpageurls.extend(urls)
                self.page_count += 1
                logger.info(
                    f"第 {self.page_count} 页列表页解析完成，新增 {len(urls)} 个职位URL，累计 {len(detailpageurls)} 个"
                )
                print(
                    f"第 {self.page_count} 页列表页解析完成，新增 {len(urls)} 个职位URL"
                )
            else:
                logger.warning("未找到职位列表")

            nextpage = soup.find("div", "searchResultPagination").find_all("a")[-1]
            delay = random.randrange(25, 45)
            logger.debug(f"随机延迟 {delay} 秒")
            time.sleep(delay)

            if spidersingle:
                self.follow(nextpage["href"], self.parse)

        except Exception as e:
            logger.error(f"列表页解析错误: {str(e)}", exc_info=True)


class detailpage(requestPage.Browser):
    def __init__(self, browser, queue):
        super(detailpage, self).__init__(browser)
        self.queue = queue

    def start_url(self):

        urls = []
        while True:
            with acquire.acquire(y_lock, x_lock):
                if len(detailpageurls):
                    alabels = detailpageurls
                    urls.extend(alabels)
                    detailpageurls.clear()
            # print('url数：%d' % len(urls))
            if len(urls):
                self.get_page(urls[0]["href"], self.parse)
                del urls[0]
                time.sleep(random.randrange(0, 4))
            else:
                # print('等待3秒...')
                time.sleep(3)

    def parse(self, response):
        # print(self.queue)
        global detailpageurls
        soup = BeautifulSoup(response, "lxml")
        jobtitle = soup.find("div", "job-brief wrap")
        jobdescribe = soup.find("div", "job-desc").find("p")
        company = soup.find("div", "company-address").find("div", "company-desc")
        companyinfo = {}
        companyinfolist = company.find_all("p")
        companyinfo["companyname"] = company.find("a").text

        companyinfo["properties"] = companyinfolist[0].text[3::]
        companyinfo["scale"] = companyinfolist[1].text[3::]
        companyinfo["industry"] = companyinfolist[2].text[3::]
        # companyinfo.update({'companyname':company.find('a').text, 'properties':companyinfolist[0].text[3::], 'scale':companyinfolist[1].text[3::], 'industruy':companyinfolist[2].text[3::]})
        item = {}
        item["job"] = jobtitle.find("h1", "job-name").text
        item["salary"] = jobtitle.find("span", "salary").text
        item["where"] = jobtitle.find("span", "where").text
        item["time"] = jobtitle.find("span", "time").text
        item["catagory"] = jobtitle.find("span", "catagory").text
        item["num"] = jobtitle.find("span", "num").text
        item["createtime"] = jobtitle.find("span", "create-time").text
        item["company"] = companyinfo
        self.queue.put(item)
        # print(dataprocess.processing)
        # print(processing.get())


def startlistpagespider():
    logger.info("列表页爬虫线程已启动")
    print("listspider已运行")
    browser = listpage("Chrome")
    browser.start_url("https://campus.liepin.com/sojob/")


def startpagespider(queue):
    logger.info("详情页爬虫线程已启动")
    print("pagespider已运行")
    browser = detailpage("Chrome", queue)
    browser.start_url()


def startspider(queue, single, processpid):
    processpid["spider"] = os.getpid()
    logger.info(f"爬虫进程启动，PID: {os.getpid()}")

    listpagespider = threading.Thread(target=startlistpagespider)
    listpagespider.start()
    getdetailpage = threading.Thread(target=startpagespider, args=(queue,))
    getdetailpage.start()

    while single["spider"]:
        time.sleep(1)
    else:
        global spidersingle
        spidersingle = False
        logger.info("收到停止信号，等待线程结束...")
        listpagespider.join(timeout=30)
        getdetailpage.join(timeout=30)
        logger.info("爬虫进程已停止")
        print("stop spider")
        single["spiderstate"] = True


if __name__ == "__main__":
    listpagespider = threading.Thread(target=startlistpagespider)
    listpagespider.start()
    getdetailpage = threading.Thread(target=startpagespider, args=())
    getdetailpage.start()
