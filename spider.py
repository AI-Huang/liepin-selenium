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
list_browser = None
detail_browser = None


class listpage(requestPage.Browser):

    def __init__(self, browser="Chrome", max_page_count=3):
        super().__init__(browser)
        self.page_count = 0
        self.max_page_count = max_page_count

    def start_url(self, starturl):
        logger.info(f"开始爬取列表页: {starturl}")
        self.get_page(starturl, self.parse)

    def parse(self, response):
        try:
            soup = BeautifulSoup(response, "lxml")
            joblist = soup.find("div", class_="campus-recommend-jobs-content")

            if joblist:
                urls = joblist.find_all("a")
                valid_urls = [
                    a for a in urls if a.get("href") and "/job/" in a.get("href")
                ]

                # 实时记录每个职位链接
                for a_tag in valid_urls:
                    url = a_tag.get("href")
                    title = a_tag.text.strip() if a_tag.text else "无标题"
                    logger.info(f"发现职位: {title} -> {url}")

                with acquire.acquire(x_lock, y_lock):
                    detailpageurls.extend(valid_urls)
                self.page_count += 1
                logger.info(
                    f"第 {self.page_count} 页列表页解析完成，新增 {len(valid_urls)} 个职位URL，累计 {len(detailpageurls)} 个"
                )
            else:
                logger.warning("未找到职位列表，尝试备用选择器")
                jobcard_divs = soup.find_all("div", class_="seo-jobcard2-common")
                if jobcard_divs:
                    urls = []
                    for div in jobcard_divs:
                        a_tag = div.find("a")
                        if a_tag and a_tag.get("href"):
                            urls.append(a_tag)
                            # 实时记录每个职位链接
                            url = a_tag.get("href")
                            title = a_tag.text.strip() if a_tag.text else "无标题"
                            logger.info(f"发现职位: {title} -> {url}")
                    with acquire.acquire(x_lock, y_lock):
                        detailpageurls.extend(urls)
                    self.page_count += 1
                    logger.info(
                        f"第 {self.page_count} 页解析完成，新增 {len(urls)} 个职位URL"
                    )

            delay = random.randrange(5, 15)
            logger.debug(f"随机延迟 {delay} 秒")
            time.sleep(delay)

            if spidersingle and self.page_count < self.max_page_count:
                self.get_page(self.driver.current_url, self.parse)

        except Exception as e:
            logger.error(f"列表页解析错误: {str(e)}", exc_info=True)


class detailpage(requestPage.Browser):
    def __init__(self, browser, queue):
        super(detailpage, self).__init__(browser)
        self.queue = queue

    def start_url(self):
        global spidersingle
        urls = []
        while spidersingle or len(urls) > 0:
            with acquire.acquire(y_lock, x_lock):
                if len(detailpageurls):
                    alabels = detailpageurls.copy()
                    urls.extend(alabels)
                    detailpageurls.clear()

            if len(urls):
                try:
                    self.get_page(urls[0]["href"], self.parse)
                    del urls[0]
                    time.sleep(random.randrange(0, 4))
                except Exception as e:
                    logger.error(f"处理详情页失败: {str(e)}")
                    if urls:
                        del urls[0]
            else:
                if not spidersingle:
                    break
                time.sleep(1)

    def parse(self, response):
        try:
            soup = BeautifulSoup(response, "lxml")

            job_title_tag = soup.find("span", class_="job-title")
            salary_tag = soup.find("span", class_="salary")
            recruit_cnt_tag = soup.find("span", class_="recruit-cnt")
            update_time_tag = soup.find("span", class_="update-time")
            title_box = soup.find("div", class_="title-box")

            if not job_title_tag:
                logger.warning("无法解析职位详情页 - 缺少职位标题")
                return

            item = {}
            item["job"] = job_title_tag.text.strip() if job_title_tag else ""
            item["salary"] = salary_tag.text.strip() if salary_tag else ""
            item["num"] = recruit_cnt_tag.text.strip() if recruit_cnt_tag else ""
            item["createtime"] = update_time_tag.text.strip() if update_time_tag else ""

            if title_box:
                title_text = title_box.text.strip()
                parts = title_text.split("·")
                if len(parts) >= 2:
                    item["where"] = ""
                else:
                    item["where"] = ""
            else:
                item["where"] = ""

            item["time"] = ""
            item["catagory"] = ""

            companyinfo = {}
            if title_box:
                title_text = title_box.text.strip()
                parts = title_text.split("·")
                if len(parts) >= 2:
                    companyinfo["companyname"] = parts[-1].strip()
                else:
                    companyinfo["companyname"] = ""
            else:
                companyinfo["companyname"] = ""

            companyinfo["properties"] = ""
            companyinfo["scale"] = ""
            companyinfo["industry"] = ""

            item["company"] = companyinfo
            self.queue.put(item)
            logger.info(f"成功解析职位: {item['job']} - {item['salary']}")

        except Exception as e:
            logger.error(f"详情页解析错误: {str(e)}", exc_info=True)


def start_listpagespider(max_page_count=3):
    global list_browser
    logger.info(f"列表页爬虫线程 listspider 已启动，最大爬取页数: {max_page_count}")
    try:
        list_browser = listpage("Chrome", max_page_count=max_page_count)
        list_browser.start_url("https://campus.liepin.com/sojob/")
    except Exception as e:
        logger.error(f"列表页爬虫线程异常: {str(e)}", exc_info=True)
    finally:
        if list_browser:
            list_browser.quit()
            logger.info("列表页浏览器已关闭")


def start_pagespider(queue):
    global detail_browser
    logger.info("详情页爬虫线程 pagespider 已启动")
    try:
        detail_browser = detailpage("Chrome", queue)
        detail_browser.start_url()
    except Exception as e:
        logger.error(f"详情页爬虫线程异常: {str(e)}", exc_info=True)
    finally:
        if detail_browser:
            detail_browser.quit()
            logger.info("详情页浏览器已关闭")


def startspider(queue, single, processpid, max_page_count=3):
    global spidersingle, list_browser, detail_browser

    processpid["spider"] = os.getpid()
    logger.info(f"爬虫进程启动，PID: {os.getpid()}")

    listpagespider = threading.Thread(
        target=start_listpagespider, args=(max_page_count,)
    )
    listpagespider.start()
    getdetailpage = threading.Thread(target=start_pagespider, args=(queue,))
    getdetailpage.start()

    try:
        while single["spider"]:
            time.sleep(1)

            # 检测是否所有页面都已爬完
            # 条件：列表页线程已结束 + 详情页线程已结束 + 队列为空
            if not listpagespider.is_alive() and not getdetailpage.is_alive():
                logger.info("所有爬虫线程已结束，自动退出")
                single["spider"] = False
                break

            # 列表页结束但详情页还在处理时，给个提示
            if not listpagespider.is_alive() and getdetailpage.is_alive():
                logger.debug("列表页爬取完成，正在处理剩余详情页...")

    except Exception as e:
        logger.error(f"主循环异常: {str(e)}", exc_info=True)
    finally:
        spidersingle = False
        logger.info("收到停止信号，等待线程结束...")

        if listpagespider.is_alive():
            listpagespider.join(timeout=30)

        if getdetailpage.is_alive():
            getdetailpage.join(timeout=30)

        logger.info("stop spider, 爬虫进程已停止")
        single["spiderstate"] = True


if __name__ == "__main__":
    listpagespider = threading.Thread(target=start_listpagespider)
    listpagespider.start()
    getdetailpage = threading.Thread(target=start_pagespider, args=())
    getdetailpage.start()
