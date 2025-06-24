from apscheduler.schedulers.blocking import BlockingScheduler
from crawler_runner import run_spider_once

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=0)  # Runs daily at midnight
def scheduled_task():
    print("Running scheduled crawl + change detection...")
    run_spider_once()

scheduler.start()
