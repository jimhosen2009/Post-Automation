"""
POST EXECUTOR
═══════════════════════════════════════════════════════════════
Wrapper for all post attempts with retry and webhook notifications.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from anime_bot.services.webhook_notifier import get_webhook_notifier
from anime_bot.models.failure_tracker import get_failure_tracker
from anime_bot.utils.retry_handler import get_retry_handler
from anime_bot.services.facebook_poster import post_to_facebook
from anime_bot.services.post_generator import generate_facebook_post
from anime_bot.services.meme_generator import get_meme_generator
from anime_bot.services.meme_collector import get_meme_collector
from anime_bot.models.database import NewsDatabase


class PostExecutor:
    """Execute posts with retry logic and webhook notifications."""
    
    def __init__(self):
        self.webhook = get_webhook_notifier()
        self.failure_tracker = get_failure_tracker()
        self.retry_handler = get_retry_handler()
        self.meme_generator = get_meme_generator()
        self.meme_collector = get_meme_collector()
        self.db = NewsDatabase()
    
    def execute_news_post(self, article: Optional[Dict] = None) -> bool:
        """Execute news post with retry logic."""
        
        def _post_news():
            # Get article if not provided
            if not article:
                from anime_bot.services.news_collector import collect_anime_news
                from anime_bot.services.content_filter import filter_and_rank
                
                articles = collect_anime_news()
                if not articles:
                    raise Exception("No articles found")
                
                filtered = filter_and_rank(articles, self.db)
                if not filtered:
                    raise Exception("No suitable articles found")
                
                article = filtered[0]  # Get best article
            
            # Generate post
            post_data = generate_facebook_post(article)
            if not post_data:
                raise Exception("Failed to generate post")
            
            # Post to Facebook
            image_url = post_data.get('image_url', '')
            success = post_to_facebook(post_data, image_url)
            
            if not success:
                raise Exception("Failed to post to Facebook")
            
            # Mark as posted
            model_used = post_data['models_used']['generation']
            self.db.mark_as_posted(post_data["article_hash"], model_used)
            
            # Notify success
            self.webhook.notify_post_success(
                post_type="news",
                title=article['title'],
                details=f"Quality: {article.get('quality_score', 0):.1f}/10, Image: {'Yes' if image_url else 'No'}"
            )
            
            return True
        
        try:
            # Notify before posting
            self.webhook.send_webhook("📰 **Executing news post...**")
            
            # Execute with retry
            result = self.retry_handler.execute_with_retry(_post_news)
            
            if result:
                print("✅ News post executed successfully")
                return True
            else:
                print("❌ News post failed after all retries")
                return False
                
        except Exception as e:
            failure_count = self.failure_tracker.increment_failure_counter()
            self.webhook.notify_error(f"News post execution failed: {str(e)}", failure_count, "news")
            return False
    
    def execute_meme_post(self) -> bool:
        """Execute meme post with retry logic."""
        
        def _post_meme():
            # Get random meme
            meme = self.meme_collector.get_random_meme(self.db)
            if not meme:
                raise Exception("No memes available")
            
            # Generate meme post
            meme_post = self.meme_generator.create_meme_post(meme)
            if not meme_post:
                raise Exception("Failed to generate meme post")
            
            # Post to Facebook
            success = post_to_facebook(meme_post, meme_post['image_url'])
            
            if not success:
                raise Exception("Failed to post meme to Facebook")
            
            # Track posted meme
            self.db.mark_as_posted(meme_post["meme_id"], "meme_generator")
            
            # Notify success
            self.webhook.notify_post_success(
                post_type="meme",
                title=meme_post['meme_name'],
                details=f"Source: {meme_post['source']}, Engagement: High"
            )
            
            return True
        
        try:
            # Notify before posting
            self.webhook.send_webhook("🎭 **Executing meme post...**")
            
            # Execute with retry
            result = self.retry_handler.execute_with_retry(_post_meme)
            
            if result:
                print("✅ Meme post executed successfully")
                return True
            else:
                print("❌ Meme post failed after all retries")
                return False
                
        except Exception as e:
            failure_count = self.failure_tracker.increment_failure_counter()
            self.webhook.notify_error(f"Meme post execution failed: {str(e)}", failure_count, "meme")
            return False
    
    def post_with_retry(self, post_func, post_data: Dict) -> bool:
        """Generic post function with retry logic."""
        
        def _execute_post():
            return post_func(post_data)
        
        try:
            result = self.retry_handler.execute_with_retry(_execute_post)
            return result is not None
            
        except Exception as e:
            failure_count = self.failure_tracker.increment_failure_counter()
            self.webhook.notify_error(f"Post execution failed: {str(e)}", failure_count)
            return False
    
    def execute_immediate_news(self) -> bool:
        """Execute immediate news post on startup."""
        try:
            self.webhook.notify_immediate_post("news", "Latest anime news")
            return self.execute_news_post()
        except Exception as e:
            failure_count = self.failure_tracker.increment_failure_counter()
            self.webhook.notify_error(f"Immediate news post failed: {str(e)}", failure_count, "news")
            return False
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get post execution statistics."""
        failure_stats = self.failure_tracker.get_failure_stats()
        meme_stats = self.meme_collector.get_meme_stats()
        
        return {
            "total_failures": failure_stats["total_failures"],
            "today_failures": failure_stats["today_failures"],
            "memes_available": meme_stats["total_fetched"],
            "apis_available": meme_stats["apis_available"],
            "last_failure": failure_stats["last_failure"]
        }


# Global post executor instance
_post_executor = None

def get_post_executor() -> PostExecutor:
    """Get global post executor instance."""
    global _post_executor
    if _post_executor is None:
        _post_executor = PostExecutor()
    return _post_executor
