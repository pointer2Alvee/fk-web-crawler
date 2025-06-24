from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.fkcrawling.fkcrawling.spiders.crawling_spider import CrawlingSpider

def run_spider_once():
    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    process.start()
