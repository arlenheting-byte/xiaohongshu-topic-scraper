"""
Task scheduler for running scraper periodically
"""
import asyncio
import logging
import schedule
import time
from datetime import datetime
from typing import List

from scraper import XiaohongshuScraper

logger = logging.getLogger(__name__)

class ScraperScheduler:
    """Schedule and manage periodic scraping tasks"""
    
    def __init__(self, use_proxy: bool = True):
        self.use_proxy = use_proxy
        self.tasks: List[dict] = []
    
    def add_daily_task(self, topics: List[str], run_time: str = "09:00"):
        """
        Add a daily scraping task
        
        Args:
            topics: List of topics to scrape
            run_time: Time to run in HH:MM format (e.g., "09:00")
        """
        self.tasks.append({
            'type': 'daily',
            'topics': topics,
            'run_time': run_time,
            'schedule_obj': schedule.every().day.at(run_time)
        })
        logger.info(f"Scheduled daily task for {topics} at {run_time}")
    
    def add_hourly_task(self, topics: List[str]):
        """
        Add an hourly scraping task
        
        Args:
            topics: List of topics to scrape
        """
        self.tasks.append({
            'type': 'hourly',
            'topics': topics,
            'schedule_obj': schedule.every().hour
        })
        logger.info(f"Scheduled hourly task for {topics}")
    
    def add_interval_task(self, topics: List[str], minutes: int):
        """
        Add a periodic scraping task at specified interval
        
        Args:
            topics: List of topics to scrape
            minutes: Interval in minutes
        """
        self.tasks.append({
            'type': 'interval',
            'topics': topics,
            'minutes': minutes,
            'schedule_obj': schedule.every(minutes).minutes
        })
        logger.info(f"Scheduled interval task for {topics} every {minutes} minutes")
    
    async def scrape_topics(self, topics: List[str]):
        """Execute scraping for given topics"""
        try:
            logger.info(f"Starting scheduled scrape for topics: {topics}")
            scraper = XiaohongshuScraper(use_proxy=self.use_proxy)
            await scraper.run(topics)
            logger.info(f"Completed scheduled scrape at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error in scheduled scrape: {e}")
    
    def schedule_jobs(self):
        """Schedule all registered jobs"""
        for task in self.tasks:
            task['schedule_obj'].do(
                asyncio.run,
                self.scrape_topics(task['topics'])
            )
    
    async def run_scheduler(self):
        """Run the scheduler"""
        logger.info("Starting scheduler...")
        self.schedule_jobs()
        
        try:
            while True:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
    
    def start(self):
        """Start scheduler (blocking)"""
        logger.info("Starting scheduler...")
        self.schedule_jobs()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

def main():
    """Example usage of scheduler"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scheduler = ScraperScheduler(use_proxy=True)
    
    # Add daily task at 9:00 AM
    scheduler.add_daily_task(['穿搭', '护肤'], run_time="09:00")
    
    # Add daily task at 3:00 PM
    scheduler.add_daily_task(['美食', '旅游'], run_time="15:00")
    
    # Add hourly task
    scheduler.add_hourly_task(['热门话题'])
    
    # Start scheduler
    scheduler.start()

if __name__ == '__main__':
    main()
