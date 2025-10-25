"""
WEBHOOK NOTIFIER
═══════════════════════════════════════════════════════════════
Discord webhook integration for bot notifications and logging.
"""

import requests
import time
from typing import Optional
from datetime import datetime

from anime_bot.config import DISCORD_WEBHOOK_URL, REQUEST_TIMEOUT


class WebhookNotifier:
    """Discord webhook notification system."""
    
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL
        self.last_message_time = 0
        self.rate_limit_delay = 1  # seconds between messages
    
    def _send_webhook(self, message: str, mention_everyone: bool = False) -> bool:
        """Send message to Discord webhook with rate limiting."""
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_message_time < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay)
            
            # Prepare message
            if mention_everyone:
                message = f"@everyone {message}"
            
            payload = {
                "content": message,
                "username": "Anime Bot",
                "avatar_url": "https://cdn.discordapp.com/emojis/1234567890123456789.png"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            self.last_message_time = time.time()
            
            if response.status_code == 200:
                return True
            else:
                print(f"Webhook error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Webhook exception: {e}")
            return False
    
    def send_webhook(self, message: str, mention_everyone: bool = False) -> bool:
        """Public method to send webhook message."""
        return self._send_webhook(message, mention_everyone)
    
    def notify_bot_started(self) -> bool:
        """Notify that bot has started."""
        message = f"🤖 **Anime Bot Started**\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self._send_webhook(message)
    
    def notify_news_scheduled(self, time_str: str) -> bool:
        """Notify that news post is scheduled."""
        message = f"📰 News post scheduled at {time_str}"
        return self._send_webhook(message, mention_everyone=True)
    
    def notify_meme_scheduled(self, time_str: str) -> bool:
        """Notify that meme post is scheduled."""
        message = f"🎭 Meme post scheduled at {time_str}"
        return self._send_webhook(message, mention_everyone=True)
    
    def notify_post_success(self, post_type: str, title: str, details: str = "") -> bool:
        """Notify successful post."""
        emoji = "📰" if post_type == "news" else "🎭"
        message = f"✅ {emoji} **{post_type.title()} posted successfully!**\n"
        message += f"Title: {title[:100]}{'...' if len(title) > 100 else ''}\n"
        if details:
            message += f"Details: {details}"
        
        return self._send_webhook(message)
    
    def notify_error(self, error: str, failure_count: int, post_type: str = "unknown") -> bool:
        """Notify error occurrence."""
        message = f"❌ **Error posting {post_type}**\n"
        message += f"Error: {error}\n"
        message += f"Total failures: {failure_count}"
        
        return self._send_webhook(message)
    
    def notify_retry_attempt(self, attempt: int, max_attempts: int, delay: int) -> bool:
        """Notify retry attempt."""
        message = f"🔄 Retry attempt: {attempt}/{max_attempts}\n"
        message += f"Next retry in: {delay} seconds"
        
        return self._send_webhook(message)
    
    def notify_reschedule(self, post_type: str, original_time: str, new_time: str, reason: str) -> bool:
        """Notify post rescheduling."""
        message = f"⏰ **Post rescheduled**\n"
        message += f"Type: {post_type.title()}\n"
        message += f"Original time: {original_time}\n"
        message += f"New time: {new_time}\n"
        message += f"Reason: {reason}"
        
        return self._send_webhook(message)
    
    def notify_daily_reset(self, meme_count: int, news_time: str) -> bool:
        """Notify daily schedule reset."""
        message = f"🌅 **Daily Schedule Reset**\n"
        message += f"Memes scheduled: {meme_count}\n"
        message += f"News scheduled: {news_time}"
        
        return self._send_webhook(message)
    
    def notify_immediate_post(self, post_type: str, title: str) -> bool:
        """Notify immediate post on startup."""
        emoji = "📰" if post_type == "news" else "🎭"
        message = f"🚀 {emoji} **Immediate {post_type.title()} Post**\n"
        message += f"Title: {title[:100]}{'...' if len(title) > 100 else ''}"
        
        return self._send_webhook(message)


# Global webhook notifier instance
_webhook_notifier = None

def get_webhook_notifier() -> WebhookNotifier:
    """Get global webhook notifier instance."""
    global _webhook_notifier
    if _webhook_notifier is None:
        _webhook_notifier = WebhookNotifier()
    return _webhook_notifier

def send_webhook(message: str, mention_everyone: bool = False) -> bool:
    """Convenience function to send webhook message."""
    return get_webhook_notifier().send_webhook(message, mention_everyone)
