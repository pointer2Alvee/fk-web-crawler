from apscheduler.schedulers.blocking import BlockingScheduler
from crawler_runner import run_spider_once
from utilities.generate_report import write_daily_change_report
scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron',
    year=None,        # e.g. 2025
    month=None,       # e.g. 1-12
    day=None,         # e.g. 1-31
    week=None,        # e.g. 1-53
    day_of_week=None, # e.g. 'mon', 'tue', ..., 'sun' or 0-6
    hour=0,           # e.g 1:15 pm => hour=13 minute=15
    minute=0
) # 0:0 => Runs daily at mid night

def scheduled_task():
    print("Running scheduled crawl + change detection...")
     
    # Step 1: Crawl the site
    run_spider_once()
    
    # Step 2: Generate daily report after crawling is done
    print("[SCHEDULER] Crawling done. Now generating change report...")
    write_daily_change_report()

    print("[SCHEDULER] Daily scheduled task completed.")


# Start the scheduler
if __name__ == "__main__":
    scheduler.start()
