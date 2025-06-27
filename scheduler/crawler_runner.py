from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.fkcrawling.fkcrawling.spiders.crawling_spider import CrawlingSpider

def run_spider_once():
    """
    Runs the Scrapy spider once using the current project settings.

    Initializes a Scrapy CrawlerProcess with settings loaded
    from the project's settings file, then schedules and starts a single
    crawl using the CrawlingSpider.

    Typically used for:
    - One-time scraping jobs
    - Manual triggering from scripts or schedulers (like APScheduler)

    Returns:
        None
    """
    process = CrawlerProcess(get_project_settings())
    process.crawl(CrawlingSpider)
    process.start()
