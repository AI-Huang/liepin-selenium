import csv
import os

from logger import logger


def start(queue, single, processpid, file_path="data/raw/data.csv"):
    processpid["savedata"] = os.getpid()
    logger.info(f"数据保存进程启动，PID: {os.getpid()}")
    logger.info(f"数据保存路径: {file_path}")
    logger.info("savedata已启动")

    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    save_count = 0
    with open(file_path, "w", newline="", encoding="utf-8") as fp:
        csvdata = csv.DictWriter(
            fp,
            [
                "job",
                "salary",
                "where",
                "time",
                "catagory",
                "num",
                "createtime",
                "companyname",
                "properties",
                "scale",
                "industry",
            ],
        )
        csvdata.writeheader()

        while single["spider"] or not queue.empty():
            try:
                data = queue.get(timeout=5)
                data.update(data["company"])
                del data["company"]
                csvdata.writerow(data)
                save_count += 1

                if save_count % 10 == 0:
                    logger.info(f"已保存 {save_count} 条职位数据")
                    print(f"已保存 {save_count} 条职位数据")

            except Exception:
                if not single["spider"] and queue.empty():
                    break
                continue

        single["savedatastate"] = True
        logger.info(f"数据保存进程已停止，共保存 {save_count} 条数据")
        print(f"stop savedata，共保存 {save_count} 条数据")


if __name__ == "__main__":
    # test()
    pass
