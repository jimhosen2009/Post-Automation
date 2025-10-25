"""
RETRY HANDLER
═══════════════════════════════════════════════════════════════
Exponential backoff retry logic with automatic recovery.
"""

import time
import random
from typing import Any, Callable, Optional, Dict
from functools import wraps

from anime_bot.config import MAX_RETRY_ATTEMPTS, RETRY_BASE_DELAY, RETRY_MAX_DELAY
from anime_bot.models.failure_tracker import get_failure_tracker
from anime_bot.services.webhook_notifier import get_webhook_notifier


def retry_with_backoff(func: Callable, max_retries: int = MAX_RETRY_ATTEMPTS, 
                      *args, **kwargs) -> Optional[Any]:
    """
    Retry function with exponential backoff.
    Returns result on success, None on failure after all retries.
    """
    failure_tracker = get_failure_tracker()
    webhook = get_webhook_notifier()
    
    for attempt in range(1, max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if result is not None:
                return result
            else:
                # Function returned None, treat as failure
                raise Exception("Function returned None")
                
        except Exception as e:
            error_msg = str(e)
            
            # Log failure
            failure_tracker.log_failure(
                error_type="retry_attempt",
                details=f"Attempt {attempt}: {error_msg}",
                retry_count=attempt
            )
            
            # Notify webhook about retry
            if attempt < max_retries:
                delay = failure_tracker.calculate_retry_delay(attempt)
                webhook.notify_retry_attempt(attempt, max_retries, delay)
                
                # Add jitter to prevent thundering herd
                jitter = random.uniform(0.1, 0.5)
                time.sleep(delay + jitter)
            else:
                # Final attempt failed
                failure_count = failure_tracker.increment_failure_counter()
                webhook.notify_error(error_msg, failure_count)
                return None
    
    return None


def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Safely execute function with retry logic.
    Never raises exceptions - returns None on failure.
    """
    try:
        return retry_with_backoff(func, *args, **kwargs)
    except Exception as e:
        failure_tracker = get_failure_tracker()
        webhook = get_webhook_notifier()
        
        failure_count = failure_tracker.increment_failure_counter()
        webhook.notify_error(f"Safe execute failed: {str(e)}", failure_count)
        return None


def reschedule_failed_post(post_type: str, post_data: Dict, 
                          scheduler_func: Callable) -> bool:
    """
    Reschedule a failed post to a later random time.
    """
    try:
        from anime_bot.scheduler import generate_random_post_time
        from datetime import datetime, timedelta
        
        # Generate new time (1-4 hours from now)
        now = datetime.now()
        delay_hours = random.uniform(1, 4)
        new_time = now + timedelta(hours=delay_hours)
        
        # Format times
        original_time = post_data.get('scheduled_time', 'unknown')
        new_time_str = new_time.strftime('%Y-%m-%d %H:%M')
        
        # Notify webhook
        webhook = get_webhook_notifier()
        webhook.notify_reschedule(
            post_type=post_type,
            original_time=original_time,
            new_time=new_time_str,
            reason="API failures after 5 retries"
        )
        
        # Schedule the post
        scheduler_func(new_time, post_data)
        
        return True
        
    except Exception as e:
        failure_tracker = get_failure_tracker()
        webhook = get_webhook_notifier()
        
        failure_count = failure_tracker.increment_failure_counter()
        webhook.notify_error(f"Reschedule failed: {str(e)}", failure_count)
        return False


def retry_decorator(max_retries: int = MAX_RETRY_ATTEMPTS):
    """
    Decorator for automatic retry with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Any]:
            return retry_with_backoff(func, max_retries, *args, **kwargs)
        return wrapper
    return decorator


class RetryHandler:
    """Advanced retry handler with custom strategies."""
    
    def __init__(self):
        self.failure_tracker = get_failure_tracker()
        self.webhook = get_webhook_notifier()
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Execute function with retry logic."""
        return retry_with_backoff(func, *args, **kwargs)
    
    def execute_safe(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Execute function safely with error handling."""
        return safe_execute(func, *args, **kwargs)
    
    def reschedule_post(self, post_type: str, post_data: Dict, 
                       scheduler_func: Callable) -> bool:
        """Reschedule failed post."""
        return reschedule_failed_post(post_type, post_data, scheduler_func)
    
    def get_retry_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        stats = self.failure_tracker.get_failure_stats()
        recent_failures = self.failure_tracker.get_recent_failures(24)
        
        return {
            "total_failures": stats["total_failures"],
            "today_failures": stats["today_failures"],
            "recent_retries": len(recent_failures),
            "failure_types": stats["failure_types"]
        }


# Global retry handler instance
_retry_handler = None

def get_retry_handler() -> RetryHandler:
    """Get global retry handler instance."""
    global _retry_handler
    if _retry_handler is None:
        _retry_handler = RetryHandler()
    return _retry_handler
