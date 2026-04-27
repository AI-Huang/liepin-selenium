import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

URL = "https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key=python"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}

JOB_CARD_CLASS = "_40108Nrnc3 job-card-pc-container"

MAX_WAIT_TIME = 10
SCROLL_DELAY = 3

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

OUTPUT_FILENAME = "liepin_jobs_{timestamp}.json"
