"""
ANIME NEWS BOT - MODULAR VERSION
═══════════════════════════════════════════════════════════════
Main entry point for the anime news bot with multi-AI engine.
"""

import time
from datetime import datetime

# Import all modules
from .ai.api import initialize_ai_system, get_health_status
from .models.database import NewsDatabase
from .services.news_collector import collect_anime_news
from .services.content_filter import filter_and_rank
from .services.post_generator import generate_facebook_post
from .services.facebook_poster import post_to_facebook
from .scheduler import get_next_run_info, wait_until_post_time, schedule_daily_memes, schedule_daily_news, run_continuous_scheduler
from .config import POST_DELAY, ENABLE_IMAGE_ATTACHMENTS, ENABLE_CONTINUOUS_MODE
from .services.webhook_notifier import get_webhook_notifier
from .services.post_executor import get_post_executor
from .models.failure_tracker import get_failure_tracker


def main():
    """Main execution - Single best post daily with image."""
    print("=" * 70)
    print("ANIME NEWS BOT - DAILY SINGLE POST WITH IMAGES")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show next run info
    next_run_info = get_next_run_info()
    print(f"Next run: {next_run_info['formatted_time']} ({next_run_info['status']})")
    
    # CRITICAL: Initialize AI system first!
    print("\n" + "="*70)
    print("STEP 1: Testing ALL AI Models")
    print("="*70)
    
    if not initialize_ai_system():
        print("\nCRITICAL: No AI models working!")
        print("   Please check your API keys and try again.")
        return
    
    # Initialize database
    db = NewsDatabase()
    
    # Collect news
    print("\n" + "="*70)
    print("STEP 2: Collecting News")
    print("="*70)
    
    articles = collect_anime_news()
    
    if not articles:
        print("\nNo articles found")
        return
    
    # Filter to get THE BEST article
    print("\n" + "="*70)
    print("STEP 3: Finding THE BEST Article")
    print("="*70)
    
    top_articles = filter_and_rank(articles, db)
    
    if not top_articles:
        print("\nNo new anime articles")
        db.update_last_run()
        return
    
    # Take only the BEST article (first one)
    best_article = top_articles[0]
    print(f"\nSelected BEST article:")
    print(f"Title: {best_article['title']}")
    print(f"Quality: {best_article['quality_score']:.1f}/10")
    print(f"Anime Confidence: {best_article['anime_confidence']:.1f}/10")
    
    # Generate post with image
    print("\n" + "="*70)
    print("STEP 4: Generating Post with Image")
    print("="*70)
    
    post_data = generate_facebook_post(best_article)
    
    if not post_data:
        print("Failed to generate post")
        db.add_failed_article(best_article)
        return
    
    # Post to Facebook with image
    print("\n" + "="*70)
    print("STEP 5: Posting to Facebook")
    print("="*70)
    
    image_url = post_data.get('image_url', '')
    if image_url and ENABLE_IMAGE_ATTACHMENTS:
        print(f"Posting with image: {image_url[:50]}...")
    else:
        print("Posting text-only")
    
    if post_to_facebook(post_data, image_url):
        # Track which model was used
        model_used = post_data['models_used']['generation']
        db.mark_as_posted(post_data["article_hash"], model_used)
        print("SUCCESS: Posted to Facebook!")
    else:
        print("FAILED: Could not post to Facebook")
        db.add_failed_article(best_article)
        return
    
    # Summary
    print("\n" + "="*70)
    print("SESSION SUMMARY")
    print("="*70)
    print(f"Posted: 1 article")
    print(f"Quality: {best_article['quality_score']:.1f}/10")
    print(f"Image: {'Yes' if image_url else 'No'}")
    print(f"Models used: {post_data['models_used']['analysis']} + {post_data['models_used']['generation']}")
    print(f"Lifetime total: {db.get_total_posts()}")
    
    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Final health status
    print(get_health_status())
    
    db.update_last_run()


def run_daily_scheduler():
    """Run the bot with daily scheduling."""
    print("=" * 70)
    print("ANIME NEWS BOT - DAILY SCHEDULER")
    print("=" * 70)
    
    # Get next run time
    next_run_info = get_next_run_info()
    print(f"Next post scheduled for: {next_run_info['formatted_time']}")
    print(f"Hours until next run: {next_run_info['hours_until']:.1f}")
    
    # Wait until post time
    wait_until_post_time()
    
    # Run the main function
    main()


def run_now():
    """Run the bot immediately (for testing)."""
    main()


def main_continuous():
    """Main continuous operation - 24/7 self-running bot."""
    print("=" * 70)
    print("ANIME BOT - CONTINUOUS AUTOMATION")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize systems
    webhook = get_webhook_notifier()
    executor = get_post_executor()
    failure_tracker = get_failure_tracker()
    
    # Notify bot started
    webhook.notify_bot_started()
    
    # Step 1: Initialize AI system
    print("\n" + "="*70)
    print("STEP 1: Testing ALL AI Models")
    print("="*70)
    
    if not initialize_ai_system():
        print("\nCRITICAL: No AI models working!")
        webhook.notify_error("No AI models working on startup", failure_tracker.get_failure_count())
        return
    
    # Step 2: Post latest news immediately
    print("\n" + "="*70)
    print("STEP 2: Posting Latest News Immediately")
    print("="*70)
    
    success = executor.execute_immediate_news()
    if not success:
        print("Failed to post immediate news, continuing anyway...")
    
    # Step 3: Schedule today's memes
    print("\n" + "="*70)
    print("STEP 3: Scheduling Today's Memes")
    print("="*70)
    
    meme_times = schedule_daily_memes()
    print(f"Scheduled {len(meme_times)} memes for today")
    
    # Step 4: Schedule tomorrow's news
    print("\n" + "="*70)
    print("STEP 4: Scheduling Tomorrow's News")
    print("="*70)
    
    news_time = schedule_daily_news()
    print(f"Scheduled news for tomorrow at {news_time.strftime('%H:%M')}")
    
    # Step 5: Run continuous scheduler
    print("\n" + "="*70)
    print("STEP 5: Starting Continuous Operation")
    print("="*70)
    print("Bot will run 24/7 with automatic scheduling")
    print("Press Ctrl+C to stop")
    
    try:
        run_continuous_scheduler()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        webhook.send_webhook("🛑 **Bot stopped by user**")
    except Exception as e:
        print(f"\nBot error: {e}")
        webhook.notify_error(f"Bot crashed: {str(e)}", failure_tracker.get_failure_count())
        # Restart automatically
        print("Restarting bot in 60 seconds...")
        time.sleep(60)
        main_continuous()


def run_continuous():
    """Run the bot in continuous mode."""
    if ENABLE_CONTINUOUS_MODE:
        main_continuous()
    else:
        print("Continuous mode disabled in config")
        main()


def run_now():
    """Run the bot immediately (for testing)."""
    main()


if __name__ == "__main__":
    import sys
    
    try:
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            if mode == "continuous" or mode == "auto":
                run_continuous()
            elif mode == "schedule" or mode == "daily":
                run_daily_scheduler()
            elif mode == "now" or mode == "test":
                run_now()
            else:
                print("Usage: python -m anime_bot.main [continuous|schedule|now]")
                print("  continuous - Run 24/7 with automatic scheduling (default)")
                print("  schedule   - Run with daily scheduling")
                print("  now        - Run immediately (for testing)")
        else:
            # Default: run continuous
            run_continuous()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
