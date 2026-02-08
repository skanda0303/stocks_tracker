from apscheduler.schedulers.background import BackgroundScheduler
from fetcher import update_all_stocks
import atexit

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 15 minutes to respect rate limits and useful enough for investors
    scheduler.add_job(func=update_all_stocks, trigger="interval", minutes=15)
    scheduler.start()
    
    # Run once immediately on startup
    # update_all_stocks() # Commented out to avoid blocking startup, handled by manual trigger or first tick
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
