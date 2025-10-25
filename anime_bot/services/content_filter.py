"""
📊 CONTENT FILTERING
═══════════════════════════════════════════════════════════════
Article filtering, ranking, and anime relevance checking.
"""

import re
import random
from typing import List, Dict, Tuple
from ..config import MIN_ARTICLE_QUALITY_SCORE, MAX_POSTS_PER_DAY, TRENDING_KEYWORDS, BORING_KEYWORDS, ANIME_KEYWORDS, MIN_ANIME_CONFIDENCE
from ..utils.text_utils import calculate_text_quality_score, extract_anime_keywords, format_article_hash
from ..ai.api import generate_text


def check_anime_relevance(article: Dict) -> Tuple[bool, float, str]:
    """
    Use AI to check if article is anime-related.
    Returns: (is_anime, confidence, model_used)
    """
    
    prompt = f"""
You are an anime expert. Is this article about Japanese ANIMATION (anime)?

Title: {article['title']}
Summary: {article['summary'][:300]}

Anime = TV anime, anime movies, anime adaptations, studios, directors, voice actors
NOT anime = manga only, games only, live-action, merchandise

Respond EXACTLY like this:
ANIME: YES or NO
CONFIDENCE: 0-100
REASON: [one sentence]
"""
    
    result, model_used = generate_text(
        prompt=prompt,
        task_type="sentiment_analysis",
        temperature=0.3
    )
    
    if not result:
        # Fallback to keyword check
        return keyword_anime_check(article), "keyword_fallback"
    
    try:
        is_anime = "YES" in result.upper().split('\n')[0]
        confidence_match = re.search(r'(\d+)', result.split('\n')[1])
        confidence = int(confidence_match.group(1)) if confidence_match else 50
        
        print(f"   🤖 [{model_used}] {'✅ ANIME' if is_anime else '❌ NOT ANIME'} ({confidence}%)")
        
        return is_anime, confidence / 100, model_used
        
    except:
        return keyword_anime_check(article), "keyword_fallback"


def keyword_anime_check(article: Dict) -> Tuple[bool, float]:
    """Fallback keyword-based check."""
    text = f"{article['title']} {article['summary']}".lower()
    
    score = extract_anime_keywords(text, ANIME_KEYWORDS)
    
    return score >= 2, min(score * 0.2, 1.0)


def analyze_emotional_engagement(article: Dict) -> Tuple[float, str]:
    """
    Analyze emotional engagement and excitement level of article.
    Returns: (engagement_score, emotion_type)
    """
    prompt = f"""
Analyze the emotional engagement and excitement level of this anime news:

Title: {article['title']}
Summary: {article['summary'][:400]}

Rate the emotional impact and excitement:
- EXCITEMENT: 0-100 (how exciting/hype is this news?)
- EMOTION: [exciting/sad/shocking/wholesome/funny/neutral]
- IMPACT: 0-100 (how big is this news for anime fans?)
- FRESHNESS: 0-100 (how new/trending is this?)

Respond EXACTLY like this:
EXCITEMENT: [0-100]
EMOTION: [emotion_type]
IMPACT: [0-100]
FRESHNESS: [0-100]
"""
    
    result, model_used = generate_text(
        prompt=prompt,
        task_type="sentiment_analysis",
        temperature=0.4
    )
    
    if not result:
        # Fallback scoring
        return calculate_fallback_engagement(article), "neutral"
    
    try:
        lines = result.strip().split('\n')
        excitement = int(re.search(r'(\d+)', lines[0]).group(1)) if re.search(r'(\d+)', lines[0]) else 50
        emotion = lines[1].split(':')[1].strip().lower() if ':' in lines[1] else "neutral"
        impact = int(re.search(r'(\d+)', lines[2]).group(1)) if re.search(r'(\d+)', lines[2]) else 50
        freshness = int(re.search(r'(\d+)', lines[3]).group(1)) if re.search(r'(\d+)', lines[3]) else 50
        
        # Calculate overall engagement score
        engagement_score = (excitement * 0.4 + impact * 0.3 + freshness * 0.3) / 100
        
        print(f"   [EMOTION] {emotion.upper()} - Excitement: {excitement}%, Impact: {impact}%, Freshness: {freshness}%")
        
        return engagement_score, emotion
        
    except:
        return calculate_fallback_engagement(article), "neutral"


def calculate_fallback_engagement(article: Dict) -> float:
    """Fallback engagement calculation based on keywords."""
    title_lower = article["title"].lower()
    summary_lower = article["summary"].lower()
    text = f"{title_lower} {summary_lower}"
    
    # High engagement keywords
    high_engagement = [
        "season 2", "season 3", "final", "ending", "premiere", "trailer", 
        "announced", "confirmed", "movie", "adaptation", "studio", "director",
        "voice actor", "cast", "release", "date", "new", "first", "debut"
    ]
    
    # Emotional keywords
    emotional_keywords = [
        "sad", "death", "passing", "tribute", "memorial", "funeral",
        "happy", "celebration", "birthday", "anniversary", "milestone",
        "shocking", "surprise", "unexpected", "breaking", "exclusive"
    ]
    
    score = 0.5  # Base score
    
    # Count high engagement keywords
    for keyword in high_engagement:
        if keyword in text:
            score += 0.1
    
    # Count emotional keywords
    for keyword in emotional_keywords:
        if keyword in text:
            score += 0.15
    
    return min(1.0, score)


def calculate_quality(article: Dict) -> float:
    """Calculate article quality score with emotional engagement."""
    base_quality = calculate_text_quality_score(
        title=article["title"],
        summary=article["summary"],
        trending_keywords=TRENDING_KEYWORDS,
        boring_keywords=BORING_KEYWORDS
    )
    
    # Add emotional engagement bonus
    engagement_score, emotion = analyze_emotional_engagement(article)
    
    # Boost score for high engagement
    if engagement_score > 0.7:
        base_quality += 1.5
    elif engagement_score > 0.5:
        base_quality += 1.0
    
    # Boost for emotional content
    if emotion in ["exciting", "shocking", "sad"]:
        base_quality += 1.0
    
    return min(10.0, base_quality)


def ensure_diversity(articles: List[Dict]) -> List[Dict]:
    """
    Ensure diversity in selected articles by avoiding similar content.
    """
    if len(articles) <= 1:
        return articles
    
    diverse_articles = [articles[0]]  # Always include the best one
    
    for article in articles[1:]:
        is_diverse = True
        
        # Check for similarity with already selected articles
        for selected in diverse_articles:
            similarity = calculate_similarity(article, selected)
            if similarity > 0.7:  # Too similar
                is_diverse = False
                break
        
        if is_diverse:
            diverse_articles.append(article)
        
        # Stop when we have enough diverse articles
        if len(diverse_articles) >= MAX_POSTS_PER_DAY:
            break
    
    return diverse_articles


def calculate_similarity(article1: Dict, article2: Dict) -> float:
    """Calculate similarity between two articles."""
    # Simple similarity based on title keywords
    title1_words = set(article1["title"].lower().split())
    title2_words = set(article2["title"].lower().split())
    
    if not title1_words or not title2_words:
        return 0.0
    
    intersection = len(title1_words.intersection(title2_words))
    union = len(title1_words.union(title2_words))
    
    return intersection / union if union > 0 else 0.0


def filter_and_rank(articles: List[Dict], db) -> List[Dict]:
    """Filter with AI anime check and ensure diversity."""
    print("\nFiltering articles with AI...")
    filtered = []
    
    # Shuffle articles to get different results each time
    random.shuffle(articles)
    
    for article in articles:
        article_hash = format_article_hash(article['title'], article['link'])
        
        if db.is_already_posted(article_hash):
            continue
        
        # AI anime check
        is_anime, confidence, model_used = check_anime_relevance(article)
        
        if not is_anime or confidence < MIN_ANIME_CONFIDENCE:
            print(f"   Skipped (not anime): {article['title'][:50]}...")
            continue
        
        quality = calculate_quality(article)
        article["quality_score"] = quality
        article["anime_confidence"] = confidence
        article["hash"] = article_hash
        
        if quality >= MIN_ARTICLE_QUALITY_SCORE:
            filtered.append(article)
    
    # Sort by quality and engagement
    filtered.sort(key=lambda x: x["quality_score"] * x["anime_confidence"], reverse=True)
    
    # Ensure diversity in final selection
    diverse_filtered = ensure_diversity(filtered)
    
    print(f"   Kept {len(diverse_filtered)} diverse articles")
    return diverse_filtered[:MAX_POSTS_PER_DAY]
