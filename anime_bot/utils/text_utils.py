"""
🧹 TEXT UTILITIES
═══════════════════════════════════════════════════════════════
Text processing and validation utilities.
"""

import re
from typing import List, Dict, Optional, Tuple


def clean_html(text: str) -> str:
    """Remove HTML tags and clean up whitespace."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def validate_post(text: str) -> bool:
    """Validate post quality and format."""
    if len(text) < 50 or len(text) > 1200:
        return False
    if "#" not in text:
        return False
    if "http" not in text.lower() and "read more" not in text.lower():
        return False
    
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    
    if not emoji_pattern.search(text):
        return False
    
    return True


def extract_anime_keywords(text: str, keywords: List[str]) -> int:
    """Count how many anime keywords are found in text."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def calculate_text_quality_score(title: str, summary: str, 
                                trending_keywords: Dict[str, float],
                                boring_keywords: Dict[str, float]) -> float:
    """Calculate quality score for an article."""
    score = 5.0
    title_lower = title.lower()
    
    # Add trending keyword bonuses
    for keyword, weight in trending_keywords.items():
        if keyword in title_lower:
            score += weight * 1.5
    
    # Subtract boring keyword penalties
    for keyword, weight in boring_keywords.items():
        if keyword in title_lower:
            score += weight
    
    # Length bonuses
    if len(title) > 60:
        score += 0.5
    if len(summary) > 100:
        score += 1.0
    
    return max(0, min(10, score))


def format_article_hash(title: str, link: str) -> str:
    """Generate a hash for article deduplication."""
    import hashlib
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()
