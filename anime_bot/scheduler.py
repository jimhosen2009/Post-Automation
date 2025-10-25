"""
SCHEDULER
═══════════════════════════════════════════════════════════════
Random daily scheduling system for anime news bot.
"""

import random
import time
import schedule
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from anime_bot.config import MIN_POST_HOUR, MAX_POST_HOUR, MIN_MEMES_PER_DAY, MAX_MEMES_PER_DAY, SCHEDULE_CHECK_INTERVAL


def generate_random_post_time() -> datetime:
    """
    Generate a random time for today's post.
    Returns datetime object for today with random hour between MIN_POST_HOUR and MAX_POST_HOUR.
    """
    today = datetime.now().date()
    
    # Generate random hour and minute
    random_hour = random.randint(MIN_POST_HOUR, MAX_POST_HOUR)
    random_minute = random.randint(0, 59)
    
    post_time = datetime.combine(today, datetime.min.time().replace(
        hour=random_hour, 
        minute=random_minute
    ))
    
    # If the time has already passed today, schedule for tomorrow
    if post_time <= datetime.now():
        post_time += timedelta(days=1)
    
    return post_time


def schedule_next_run() -> datetime:
    """
    Schedule the next random run and return the scheduled time.
    """
    next_run_time = generate_random_post_time()
    
    print(f"\nScheduling next run for: {next_run_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Schedule the job
    schedule.every().day.at(next_run_time.strftime('%H:%M')).do(
        lambda: print(f"Bot should run now! ({datetime.now()})")
    )
    
    return next_run_time


def wait_until_post_time(target_time: Optional[datetime] = None) -> None:
    """
    Wait until the scheduled post time.
    If no target_time provided, generates a random one.
    """
    if target_time is None:
        target_time = generate_random_post_time()
    
    print(f"Waiting until {target_time.strftime('%Y-%m-%d %H:%M')}...")
    
    while datetime.now() < target_time:
        time.sleep(60)  # Check every minute
        remaining = target_time - datetime.now()
        if remaining.total_seconds() > 3600:  # More than 1 hour
            print(f"   {remaining.total_seconds()/3600:.1f} hours remaining...")
        elif remaining.total_seconds() > 60:  # More than 1 minute
            print(f"   {remaining.total_seconds()/60:.0f} minutes remaining...")
    
    print("   Time to post!")


def create_windows_task() -> bool:
    """
    Create a Windows Task Scheduler entry for the bot.
    This is a placeholder - actual implementation would use Windows Task Scheduler API.
    """
    try:
        # This would use subprocess to create Windows task
        # For now, just return True as a placeholder
        print("   Windows Task Scheduler integration not implemented yet")
        print("   Use wait_until_post_time() for now")
        return True
    except Exception as e:
        print(f"   Error creating Windows task: {e}")
        return False


def get_next_run_info() -> Dict:
    """
    Get information about the next scheduled run.
    """
    next_run = generate_random_post_time()
    now = datetime.now()
    
    if next_run.date() == now.date():
        status = "Today"
    elif next_run.date() == (now + timedelta(days=1)).date():
        status = "Tomorrow"
    else:
        status = f"{next_run.strftime('%Y-%m-%d')}"
    
    return {
        "next_run_time": next_run,
        "status": status,
        "hours_until": (next_run - now).total_seconds() / 3600,
        "formatted_time": next_run.strftime('%Y-%m-%d %H:%M')
    }


def schedule_daily_memes(count: int = None) -> List[datetime]:
    """
    Schedule 3-5 memes for today at random times.
    Returns list of scheduled times.
    """
    if count is None:
        count = random.randint(MIN_MEMES_PER_DAY, MAX_MEMES_PER_DAY)
    
    scheduled_times = []
    
    for i in range(count):
        # Generate random time
        random_hour = random.randint(MIN_POST_HOUR, MAX_POST_HOUR)
        random_minute = random.randint(0, 59)
        
        today = datetime.now().date()
        post_time = datetime.combine(today, datetime.min.time().replace(
            hour=random_hour, 
            minute=random_minute
        ))
        
        # If time has passed, schedule for tomorrow
        if post_time <= datetime.now():
            post_time += timedelta(days=1)
        
        # Schedule the meme post
        schedule.every().day.at(post_time.strftime('%H:%M')).do(
            lambda: _execute_meme_post()
        )
        
        scheduled_times.append(post_time)
        
        # Notify webhook
        from anime_bot.services.webhook_notifier import get_webhook_notifier
        webhook = get_webhook_notifier()
        webhook.notify_meme_scheduled(post_time.strftime('%Y-%m-%d %H:%M'))
    
    print(f"Scheduled {count} memes for today")
    return scheduled_times


def schedule_daily_news() -> datetime:
    """
    Schedule 1 news post for tomorrow at random time.
    Returns scheduled time.
    """
    # Generate random time for tomorrow
    tomorrow = datetime.now().date() + timedelta(days=1)
    random_hour = random.randint(MIN_POST_HOUR, MAX_POST_HOUR)
    random_minute = random.randint(0, 59)
    
    post_time = datetime.combine(tomorrow, datetime.min.time().replace(
        hour=random_hour, 
        minute=random_minute
    ))
    
    # Schedule the news post
    schedule.every().day.at(post_time.strftime('%H:%M')).do(
        lambda: _execute_news_post()
    )
    
    # Notify webhook
    from anime_bot.services.webhook_notifier import get_webhook_notifier
    webhook = get_webhook_notifier()
    webhook.notify_news_scheduled(post_time.strftime('%Y-%m-%d %H:%M'))
    
    print(f"Scheduled news for tomorrow at {post_time.strftime('%H:%M')}")
    return post_time


def _execute_meme_post():
    """Execute meme post (called by scheduler)."""
    try:
        from anime_bot.services.post_executor import get_post_executor
        executor = get_post_executor()
        executor.execute_meme_post()
    except Exception as e:
        print(f"Error executing scheduled meme post: {e}")


def _execute_news_post():
    """Execute news post (called by scheduler)."""
    try:
        from anime_bot.services.post_executor import get_post_executor
        executor = get_post_executor()
        executor.execute_news_post()
    except Exception as e:
        print(f"Error executing scheduled news post: {e}")


def reset_daily_schedule():
    """Clear all scheduled jobs and prepare for new day."""
    schedule.clear()
    print("Daily schedule reset")


def get_scheduled_jobs() -> List[Dict]:
    """Get list of currently scheduled jobs."""
    jobs = []
    for job in schedule.jobs:
        jobs.append({
            'next_run': job.next_run,
            'interval': job.interval,
            'unit': job.unit,
            'at_time': job.at_time
        })
    return jobs


def is_new_day() -> bool:
    """Check if it's a new day (after midnight)."""
    now = datetime.now()
    return now.hour == 0 and now.minute < 5  # Within first 5 minutes of day


def run_continuous_scheduler():
    """Run continuous scheduler with daily reset."""
    print("Starting continuous scheduler...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Check for scheduled jobs
            schedule.run_pending()
            
            # Check if new day
            if is_new_day():
                print("New day detected - resetting schedule")
                reset_daily_schedule()
                
                # Schedule new memes and news
                meme_times = schedule_daily_memes()
                news_time = schedule_daily_news()
                
                # Notify webhook
                from anime_bot.services.webhook_notifier import get_webhook_notifier
                webhook = get_webhook_notifier()
                webhook.notify_daily_reset(len(meme_times), news_time.strftime('%H:%M'))
            
            time.sleep(SCHEDULE_CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
    except Exception as e:
        print(f"Scheduler error: {e}")
        # Continue running even on error
        time.sleep(60)
        run_continuous_scheduler()


def run_scheduler_loop() -> None:
    """
    Run the scheduler in a loop, checking every minute.
    This is for continuous operation.
    """
    print("Starting scheduler loop...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
