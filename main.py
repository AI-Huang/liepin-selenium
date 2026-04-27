import multiprocessing
import time

import savefile
import showdata
import spider
from logger import logger

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("猎聘校园招聘爬虫系统启动")
    logger.info("=" * 60)
    print("Program Started...")

    pool = multiprocessing.Pool(2)
    manager = multiprocessing.Manager()
    data = manager.Queue()
    # save = manager.Queue()
    pidlist = manager.dict()
    single = manager.dict()
    single.update({"spider": True, "spiderstate": False, "savedatastate": False})
    spiderProcess = pool.apply_async(
        spider.startspider,
        (
            data,
            single,
            pidlist,
        ),
    )
    # dataProcess = pool.apply_async(dataprocess.start, (data, save, single, pidlist,))
    savefileProcess = pool.apply_async(
        savefile.start,
        (
            data,
            single,
            pidlist,
        ),
    )
    time.sleep(3)
    print("ProcessPID" + str(pidlist))
    while single["spider"]:
        key = input("输入<q>退出:")
        if key == "q":

            single["spider"] = False
            # time.sleep(20)
            # os.kill(pidlist[spider])
            # time.sleep(20)
            while single["savedatastate"] == False:
                pass
            showdata.draw()
            print("quit")
