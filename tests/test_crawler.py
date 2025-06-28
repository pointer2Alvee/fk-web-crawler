from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawler.fkcrawling.fkcrawling.spiders.crawling_spider import CrawlingSpider

def test_scraper_runs():
    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    try:
        process.start(stop_after_crawl=True)
        assert True
    except Exception:
        assert False, "Scraper failed to run"
