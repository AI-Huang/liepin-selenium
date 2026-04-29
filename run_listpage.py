import argparse
import multiprocessing
import signal
import sys
import time

import savefile
import showdata
from liepin_selenium.spiders import listpage_spider
from logger import logger


def signal_handler(signum, frame):
    logger.info(f"收到信号 {signum}，正在退出...")

    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="猎聘校园招聘爬虫")
    parser.add_argument("--pages", type=int, default=3, help="最大爬取页数（默认: 3）")
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/data.csv",
        help="输出文件路径（默认: data/raw/data.csv）",
    )
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=" * 60)
    logger.info("猎聘校园招聘爬虫系统启动")
    logger.info(f"最大爬取页数: {args.pages}")
    logger.info(f"输出文件路径: {args.output}")
    logger.info("=" * 60)

    pool = multiprocessing.Pool(2)
    manager = multiprocessing.Manager()
    data = manager.Queue()
    pidlist = manager.dict()
    single = manager.dict()
    single.update({"spider": True, "spiderstate": False, "savedatastate": False})

    try:
        spiderProcess = pool.apply_async(
            listpage_spider.startspider,
            (data, single, pidlist, args.pages),
        )
        savefileProcess = pool.apply_async(
            savefile.start,
            (data, single, pidlist, args.output),
        )

        time.sleep(3)
        logger.info("ProcessPID" + str(pidlist))

        while single["spider"]:
            try:
                key = input("输入<q>退出:")
                if key == "q":
                    single["spider"] = False
                    break
            except (EOFError, KeyboardInterrupt):
                logger.info("用户强制退出")
                single["spider"] = False
                break

        logger.info("等待爬虫进程结束...")
        while not single.get("spiderstate", False) or not single.get(
            "savedatastate", False
        ):
            time.sleep(1)

        if not data.empty():
            logger.info(f"队列中还有 {data.qsize()} 条数据等待处理")
            time.sleep(2)

        logger.info("关闭进程池...")
        pool.close()
        pool.join()

        logger.info("尝试生成可视化图表...")
        try:
            showdata.draw()
        except Exception as e:
            logger.warning(f"生成图表失败: {e}")

        logger.info("=" * 60)
        logger.info("猎聘校园招聘爬虫系统已退出")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"主程序异常: {e}", exc_info=True)
        single["spider"] = False
        pool.terminate()
        pool.join()
        sys.exit(1)
