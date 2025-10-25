"""
MEME COLLECTOR
═══════════════════════════════════════════════════════════════
Fetch anime memes from free APIs with duplicate tracking.
"""

import requests
import random
from typing import List, Dict, Optional
from datetime import datetime

from anime_bot.config import MEME_API_URLS, REQUEST_TIMEOUT


class MemeCollector:
    """Collect anime memes from free APIs."""
    
    def __init__(self):
        self.api_urls = MEME_API_URLS
        self.posted_memes = set()  # Track posted meme URLs
    
    def fetch_anime_memes(self) -> List[Dict]:
        """Fetch anime memes from all available APIs."""
        all_memes = []
        
        for api_url in self.api_urls:
            try:
                memes = self._fetch_from_api(api_url)
                if memes:
                    all_memes.extend(memes)
            except Exception as e:
                print(f"Error fetching from {api_url}: {e}")
                continue
        
        return all_memes
    
    def _fetch_from_api(self, api_url: str) -> List[Dict]:
        """Fetch memes from a specific API."""
        try:
            response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code != 200:
                print(f"API error {response.status_code} from {api_url}")
                return []
            
            data = response.json()
            
            # Handle different API response formats
            if 'memes' in data:
                # Imgflip format
                return self._parse_imgflip_response(data)
            elif 'url' in data:
                # Meme API format (single meme)
                return [self._parse_meme_api_response(data)]
            elif isinstance(data, list):
                # List format
                return [self._parse_meme_api_response(item) for item in data]
            else:
                print(f"Unknown API response format from {api_url}")
                return []
                
        except Exception as e:
            print(f"Exception fetching from {api_url}: {e}")
            return []
    
    def _parse_imgflip_response(self, data: Dict) -> List[Dict]:
        """Parse Imgflip API response."""
        memes = []
        
        for meme_data in data.get('memes', []):
            meme = {
                'id': meme_data.get('id', ''),
                'name': meme_data.get('name', ''),
                'url': meme_data.get('url', ''),
                'width': meme_data.get('width', 0),
                'height': meme_data.get('height', 0),
                'box_count': meme_data.get('box_count', 0),
                'source': 'imgflip',
                'fetched_at': datetime.now().isoformat()
            }
            
            if self.validate_meme(meme):
                memes.append(meme)
        
        return memes
    
    def _parse_meme_api_response(self, data: Dict) -> Dict:
        """Parse Meme API response."""
        meme = {
            'id': data.get('postLink', ''),
            'name': data.get('title', ''),
            'url': data.get('url', ''),
            'width': data.get('width', 0),
            'height': data.get('height', 0),
            'box_count': 2,  # Assume 2 boxes for most memes
            'source': 'meme_api',
            'fetched_at': datetime.now().isoformat(),
            'subreddit': data.get('subreddit', ''),
            'author': data.get('author', ''),
            'ups': data.get('ups', 0)
        }
        
        return meme
    
    def get_random_meme(self, db) -> Optional[Dict]:
        """Get a random anime meme that hasn't been posted."""
        memes = self.fetch_anime_memes()
        
        if not memes:
            print("No memes fetched from APIs")
            return None
        
        # Filter out already posted memes
        available_memes = [
            meme for meme in memes 
            if meme['url'] not in self.posted_memes
        ]
        
        if not available_memes:
            print("All memes have been posted, resetting posted list")
            self.posted_memes.clear()
            available_memes = memes
        
        # Select random meme
        selected_meme = random.choice(available_memes)
        
        # Mark as posted
        self.posted_memes.add(selected_meme['url'])
        
        return selected_meme
    
    def validate_meme(self, meme: Dict) -> bool:
        """Validate meme data."""
        required_fields = ['url', 'name']
        
        # Check required fields
        for field in required_fields:
            if not meme.get(field):
                return False
        
        # Check URL format
        url = meme['url']
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Check image dimensions (avoid too small images)
        width = meme.get('width', 0)
        height = meme.get('height', 0)
        
        if width < 200 or height < 200:
            return False
        
        # Check for anime-related keywords in name
        anime_keywords = [
            'anime', 'manga', 'otaku', 'weeb', 'kawaii', 'senpai',
            'waifu', 'husbando', 'shounen', 'shoujo', 'seinen', 'josei',
            'isekai', 'mecha', 'slice of life', 'romance', 'action',
            'adventure', 'comedy', 'drama', 'fantasy', 'sci-fi'
        ]
        
        name_lower = meme['name'].lower()
        if any(keyword in name_lower for keyword in anime_keywords):
            return True
        
        # If no anime keywords, still accept if from anime subreddit
        subreddit = meme.get('subreddit', '').lower()
        anime_subreddits = [
            'animemes', 'animemes', 'anime', 'manga', 'otaku',
            'anime_irl', 'animenocontext', 'wholesomeanimemes'
        ]
        
        return any(sub in subreddit for sub in anime_subreddits)
    
    def get_meme_stats(self) -> Dict[str, int]:
        """Get meme collection statistics."""
        return {
            'total_fetched': len(self.posted_memes),
            'apis_available': len(self.api_urls),
            'posted_count': len(self.posted_memes)
        }
    
    def reset_posted_memes(self) -> None:
        """Reset posted memes list (for testing or daily reset)."""
        self.posted_memes.clear()


# Global meme collector instance
_meme_collector = None

def get_meme_collector() -> MemeCollector:
    """Get global meme collector instance."""
    global _meme_collector
    if _meme_collector is None:
        _meme_collector = MemeCollector()
    return _meme_collector
