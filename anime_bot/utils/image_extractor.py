"""
🖼️ IMAGE EXTRACTION
═══════════════════════════════════════════════════════════════
Hybrid image extraction system for anime news posts.
"""

import re
import requests
import json
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from ..config import (
    ENABLE_IMAGE_ATTACHMENTS, IMAGE_EXTRACTION_PRIORITY, 
    FALLBACK_IMAGE_APIS, IMAGE_QUALITY_CHECK, MAX_IMAGE_SIZE_MB,
    MAL_API_BASE, ANILIST_API_URL
)


def extract_image_from_article(article: Dict) -> Optional[str]:
    """
    Extract image from article RSS feed or HTML content.
    Priority: RSS media content > HTML og:image > HTML img tags
    """
    if not ENABLE_IMAGE_ATTACHMENTS:
        return None
    
    # Method 1: Check RSS feed for media content
    image_url = _extract_from_rss_feed(article)
    if image_url and validate_image_url(image_url):
        return image_url
    
    # Method 2: Parse article HTML for og:image
    image_url = _extract_from_html_meta(article)
    if image_url and validate_image_url(image_url):
        return image_url
    
    # Method 3: Look for img tags in summary
    image_url = _extract_from_summary_images(article)
    if image_url and validate_image_url(image_url):
        return image_url
    
    return None


def _extract_from_rss_feed(article: Dict) -> Optional[str]:
    """Extract image from RSS feed media content."""
    # This would require modifying the RSS parser to include media content
    # For now, return None as most RSS feeds don't include images
    return None


def _extract_from_html_meta(article: Dict) -> Optional[str]:
    """Extract image from article HTML meta tags."""
    try:
        # Try to fetch the article page
        response = requests.get(article["link"], timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for og:image meta tag
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Look for twitter:image meta tag
        twitter_image = soup.find('meta', name='twitter:image')
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        return None
        
    except Exception:
        return None


def _extract_from_summary_images(article: Dict) -> Optional[str]:
    """Extract image URLs from article summary HTML."""
    try:
        soup = BeautifulSoup(article["summary"], 'html.parser')
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src')
            if src:
                # Convert relative URLs to absolute
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(article["link"], src)
                
                return src
        
        return None
        
    except Exception:
        return None


def search_anime_cover_art(title: str) -> Optional[str]:
    """
    Search for anime cover art using free APIs.
    Try MyAnimeList first, then AniList.
    """
    if not title:
        return None
    
    # Extract anime title from article title
    anime_title = _extract_anime_title(title)
    if not anime_title:
        return None
    
    # Try MyAnimeList API first
    image_url = _search_mal_api(anime_title)
    if image_url:
        return image_url
    
    # Try AniList API
    image_url = _search_anilist_api(anime_title)
    if image_url:
        return image_url
    
    return None


def _extract_anime_title(text: str) -> Optional[str]:
    """Extract anime title from article title."""
    # Remove common news words
    text = re.sub(r'\b(season|episode|anime|manga|announced|confirmed|trailer|premiere)\b', '', text, flags=re.IGNORECASE)
    
    # Look for quoted titles
    quoted_match = re.search(r'"([^"]+)"', text)
    if quoted_match:
        return quoted_match.group(1).strip()
    
    # Look for titles with colons
    colon_match = re.search(r'^([^:]+):', text)
    if colon_match:
        return colon_match.group(1).strip()
    
    # Take first part before common separators
    separators = [' - ', ' | ', ' Announces', ' Confirmed', ' Trailer']
    for sep in separators:
        if sep in text:
            return text.split(sep)[0].strip()
    
    # Return first few words
    words = text.split()[:4]
    return ' '.join(words) if words else None


def _search_mal_api(anime_title: str) -> Optional[str]:
    """Search MyAnimeList API for anime cover art."""
    try:
        url = f"{MAL_API_BASE}/anime"
        params = {'q': anime_title, 'limit': 1}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        if data.get('data') and len(data['data']) > 0:
            anime = data['data'][0]
            images = anime.get('images', {})
            jpg_image = images.get('jpg', {})
            return jpg_image.get('large_image_url')
        
        return None
        
    except Exception:
        return None


def _search_anilist_api(anime_title: str) -> Optional[str]:
    """Search AniList GraphQL API for anime cover art."""
    try:
        query = """
        query ($search: String) {
          Media(search: $search, type: ANIME) {
            coverImage {
              large
            }
          }
        }
        """
        
        variables = {'search': anime_title}
        
        response = requests.post(
            ANILIST_API_URL,
            json={'query': query, 'variables': variables},
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if data.get('data') and data['data'].get('Media'):
            media = data['data']['Media']
            cover_image = media.get('coverImage', {})
            return cover_image.get('large')
        
        return None
        
    except Exception:
        return None


def get_fallback_anime_image(emotion: str) -> str:
    """
    Get fallback anime image based on emotion.
    Uses free anime image APIs.
    """
    try:
        # Choose API based on emotion
        if emotion in ['exciting', 'shocking', 'hype']:
            api_url = FALLBACK_IMAGE_APIS[0]  # waifu.pics
        else:
            api_url = FALLBACK_IMAGE_APIS[1]  # nekos.best
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract image URL from response
            if 'url' in data:
                return data['url']
            elif 'results' in data and len(data['results']) > 0:
                return data['results'][0].get('url', '')
        
        # Fallback to a default anime image
        return "https://via.placeholder.com/400x300/FF6B9D/FFFFFF?text=Anime+News"
        
    except Exception:
        return "https://via.placeholder.com/400x300/FF6B9D/FFFFFF?text=Anime+News"


def validate_image_url(url: str) -> bool:
    """Validate image URL and check if it's accessible."""
    if not url or not IMAGE_QUALITY_CHECK:
        return True
    
    try:
        # Check URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check if it's an image URL
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if not any(url.lower().endswith(ext) for ext in image_extensions):
            # Might still be valid if it's a CDN URL
            pass
        
        # Quick HEAD request to check if image exists
        response = requests.head(url, timeout=5)
        if response.status_code != 200:
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            return False
        
        # Check file size
        content_length = response.headers.get('content-length')
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > MAX_IMAGE_SIZE_MB:
                return False
        
        return True
        
    except Exception:
        return False


def get_best_image(article: Dict, emotion: str) -> str:
    """
    Get the best image for an article using hybrid approach.
    Returns image URL or fallback.
    """
    if not ENABLE_IMAGE_ATTACHMENTS:
        return ""
    
    # Try each method in priority order
    for method in IMAGE_EXTRACTION_PRIORITY:
        image_url = None
        
        if method == "article":
            image_url = extract_image_from_article(article)
        elif method == "cover_art":
            image_url = search_anime_cover_art(article["title"])
        elif method == "fallback_api":
            image_url = get_fallback_anime_image(emotion)
        
        if image_url and validate_image_url(image_url):
            print(f"   [IMAGE] Found via {method}: {image_url[:50]}...")
            return image_url
    
    # Ultimate fallback
    fallback_url = get_fallback_anime_image(emotion)
    print(f"   [IMAGE] Using fallback: {fallback_url[:50]}...")
    return fallback_url
