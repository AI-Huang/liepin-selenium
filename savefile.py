import csv
import os

import showdata
from logger import logger

# testdata = {'job':'猎聘','num':1, 'calagory':'a', 'where':'北京', 'time':1, 'salary':1, 'createtime':1}
#
# def test():
#     with open('data.csv', 'w', newline='') as csvfp:
#         csvdata = csv.writer(csvfp)
#         while True:
#             csvdata.writerow(list(testdata.values()))
#             csvdata.writerow(['Spam'] * 5 + ['Baked Beans'])
#             csvdata.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])


def start(queue, single, processpid):
    processpid["savedata"] = os.getpid()
    logger.info(f"数据保存进程启动，PID: {os.getpid()}")
    print("savedata已启动")

    os.makedirs("data/raw", exist_ok=True)
    save_count = 0
    with open("data/raw/data.csv", "w", newline="", encoding="utf-8") as fp:
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
