import pytest

from src.liepin_crawler import JobParser, LiepinCrawler


def test_job_parser_extract():
    html = """
    <div class="_40108Nrnc3 job-card-pc-container">
        <a href="https://www.liepin.com/job/123456.shtml">Python工程师【北京】15-25k3-5年本科</a>
    </div>
    """
    cards = JobParser.parse(html)
    assert len(cards) == 1
    
    job_info = JobParser.extract_job_info(cards[0])
    assert job_info is not None
    assert job_info["title"] == "Python工程师"
    assert job_info["location"] == "北京"
    assert "15-25k" in job_info["salary"]


def test_crawler_initialization():
    crawler = LiepinCrawler(headless=True)
    assert crawler is not None
    assert crawler.jobs == []