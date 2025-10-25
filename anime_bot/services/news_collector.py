"""
🔍 NEWS COLLECTION
═══════════════════════════════════════════════════════════════
RSS feed collection and article parsing.
"""

import feedparser
import random
from typing import List, Dict
from ..config import ANIME_NEWS_SOURCES
from ..utils.text_utils import clean_html


def collect_anime_news() -> List[Dict]:
    """Fetch anime news from RSS sources with diversity focus."""
    print("\nCollecting anime news...")
    all_articles = []
    
    # Shuffle sources to get different results each time
    shuffled_sources = ANIME_NEWS_SOURCES.copy()
    random.shuffle(shuffled_sources)
    
    for feed_url in shuffled_sources:
        try:
            print(f"   {feed_url}")
            feed = feedparser.parse(feed_url)
            
            # Get more articles but with variety
            entries = feed.entries[:20]  # Get more articles
            random.shuffle(entries)  # Shuffle for variety
            
            for entry in entries[:15]:  # Still limit to 15 per source
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": clean_html(entry.get("summary", entry.get("description", ""))),
                    "source": feed_url,
                    "published": entry.get("published", ""),
                    "published_parsed": entry.get("published_parsed", None)
                }
                all_articles.append(article)
            
            print(f"   Found {len(entries[:15])} articles")
            
        except Exception as e:
            print(f"   Error: {e}")
    
    # Shuffle all articles for maximum diversity
    random.shuffle(all_articles)
    
    print(f"\nTotal: {len(all_articles)} articles")
    return all_articles
