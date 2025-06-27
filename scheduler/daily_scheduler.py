from apscheduler.schedulers.blocking import BlockingScheduler
from crawler_runner import run_spider_once

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron',
    year=None,        # e.g. 2025
    month=None,       # e.g. 1-12
    day=None,         # e.g. 1-31
    week=None,        # e.g. 1-53
    day_of_week=None, # e.g. 'mon', 'tue', ..., 'sun' or 0-6
    hour=0,
    minute=41
) # Runs daily at 12:21 AM

def scheduled_task():
    print("Running scheduled crawl + change detection...")
    run_spider_once()

scheduler.start()
