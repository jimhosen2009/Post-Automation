"""
📦 DATABASE
═══════════════════════════════════════════════════════════════
NewsDatabase class for managing article storage and analytics.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from ..config import DATABASE_FILE


class NewsDatabase:
    """Manages article storage, deduplication, and analytics."""
    
    def __init__(self, filepath: str = DATABASE_FILE):
        self.filepath = filepath
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load database from file or create new structure."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "posted_hashes": [],
                "failed_articles": [],
                "analytics": {
                    "total_posts": 0,
                    "posts_by_model": {},
                    "last_run": None
                }
            }
    
    def _save(self):
        """Save database to file."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def is_already_posted(self, article_hash: str) -> bool:
        """Check if article has already been posted."""
        return article_hash in self.data["posted_hashes"]
    
    def mark_as_posted(self, article_hash: str, model_used: str = None):
        """Mark article as posted and update analytics."""
        if article_hash not in self.data["posted_hashes"]:
            self.data["posted_hashes"].append(article_hash)
            self.data["analytics"]["total_posts"] += 1
            
            # Track which model was used
            if model_used:
                posts_by_model = self.data["analytics"]["posts_by_model"]
                posts_by_model[model_used] = posts_by_model.get(model_used, 0) + 1
            
            self._save()
    
    def add_failed_article(self, article: dict):
        """Add article to failed list for retry later."""
        self.data["failed_articles"].append({
            "article": article,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def get_failed_articles(self) -> List[dict]:
        """Get list of failed articles."""
        return self.data["failed_articles"]
    
    def clear_failed_article(self, index: int):
        """Remove failed article by index."""
        if 0 <= index < len(self.data["failed_articles"]):
            self.data["failed_articles"].pop(index)
            self._save()
    
    def update_last_run(self):
        """Update last run timestamp."""
        self.data["analytics"]["last_run"] = datetime.now().isoformat()
        self._save()
    
    def get_analytics(self) -> Dict:
        """Get analytics data."""
        return self.data["analytics"]
    
    def get_posts_by_model(self) -> Dict[str, int]:
        """Get post count by AI model."""
        return self.data["analytics"]["posts_by_model"]
    
    def get_total_posts(self) -> int:
        """Get total number of posts made."""
        return self.data["analytics"]["total_posts"]
