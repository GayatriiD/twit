"""Scheduler service for automatic tweet fetching."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import os

class SchedulerService:
    """Service for scheduling periodic tasks."""
    
    def __init__(self, twitter_service, db_session_factory):
        """
        Initialize scheduler service.
        
        Args:
            twitter_service: TwitterService instance
            db_session_factory: Function to create database sessions
        """
        self.scheduler = BackgroundScheduler()
        self.twitter_service = twitter_service
        self.db_session_factory = db_session_factory
        self.refresh_interval_hours = int(os.getenv("REFRESH_INTERVAL_HOURS", "1"))
    
    def fetch_tweets_job(self):
        """Job to fetch tweets from all active handles."""
        print(f"[{datetime.now()}] Running scheduled tweet fetch...")
        
        # Create a new database session for this job
        db = self.db_session_factory()
        try:
            stats = self.twitter_service.fetch_and_store_tweets(db)
            print(f"[{datetime.now()}] Scheduled fetch complete: {stats}")
        except Exception as e:
            print(f"Error in scheduled fetch: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the scheduler."""
        # Add job to run every N hours
        self.scheduler.add_job(
            func=self.fetch_tweets_job,
            trigger=IntervalTrigger(hours=self.refresh_interval_hours),
            id='fetch_tweets_job',
            name='Fetch tweets from active handles',
            replace_existing=True
        )
        
        # Run immediately on startup
        self.fetch_tweets_job()
        
        # Start scheduler
        self.scheduler.start()
        print(f"Scheduler started - will fetch tweets every {self.refresh_interval_hours} hour(s)")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Scheduler stopped")
    
    def trigger_manual_fetch(self):
        """Manually trigger a tweet fetch."""
        self.fetch_tweets_job()
