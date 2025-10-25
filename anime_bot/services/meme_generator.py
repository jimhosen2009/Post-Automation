"""
MEME GENERATOR
═══════════════════════════════════════════════════════════════
AI-powered meme caption generation for anime memes.
"""

import random
from typing import Optional, Dict

from anime_bot.ai.api import generate_text
from anime_bot.services.webhook_notifier import get_webhook_notifier


class MemeGenerator:
    """Generate AI-powered captions for anime memes."""
    
    def __init__(self):
        self.webhook = get_webhook_notifier()
    
    def generate_meme_caption(self, meme_context: str, image_url: str) -> str:
        """Generate funny caption for anime meme."""
        
        # Extract meme name/title for context
        meme_name = meme_context.get('name', 'anime meme')
        meme_source = meme_context.get('source', 'unknown')
        
        # Create AI prompt for caption generation
        prompt = f"""
You are a VIRAL anime meme caption generator! Create a funny, relatable caption for this anime meme.

MEME INFO:
- Name: {meme_name}
- Source: {meme_source}
- Image URL: {image_url}

CAPTION REQUIREMENTS:
✅ Make it FUNNY and relatable to anime fans
✅ Keep it SHORT (1-2 sentences max)
✅ Use anime/manga references if relevant
✅ Make it VIRAL and shareable
✅ Add appropriate emojis
✅ Use casual, fan language (not corporate)

CAPTION STYLES (pick one randomly):
- Relatable anime fan experience
- Funny anime trope reference
- Wholesome anime moment
- Dramatic anime scene parody
- Cute anime character reference

EXAMPLES:
- "When you finally understand the plot after 12 episodes 😭"
- "Me trying to explain anime to my parents 🗿"
- "That one character everyone loves but you don't get why 🤔"
- "When the anime ends but the manga continues 📚"

Create ONE funny caption (just the caption, nothing else):
"""
        
        try:
            caption, model_used = generate_text(
                prompt=prompt,
                task_type="creative_writing",
                temperature=0.9
            )
            
            if caption:
                # Clean up the caption
                caption = caption.strip()
                if caption.startswith('"') and caption.endswith('"'):
                    caption = caption[1:-1]
                
                print(f"   Generated meme caption by: {model_used}")
                return caption
            else:
                return self._get_fallback_caption(meme_name)
                
        except Exception as e:
            print(f"   Error generating caption: {e}")
            return self._get_fallback_caption(meme_name)
    
    def _get_fallback_caption(self, meme_name: str) -> str:
        """Get fallback caption if AI generation fails."""
        fallback_captions = [
            "When you realize anime is life 🎌",
            "This hits different at 3 AM 🌙",
            "Anime fans unite! 🤝",
            "The struggle is real 😭",
            "Why is this so accurate? 🤔",
            "Me watching anime instead of sleeping 😴",
            "Anime logic be like... 🤯",
            "When the plot twist hits different 🔥",
            "This is why we love anime 💕",
            "Anime fans will understand 🎯"
        ]
        
        return random.choice(fallback_captions)
    
    def create_meme_post(self, meme: Dict) -> Optional[Dict]:
        """Create complete meme post with caption."""
        
        print(f"\nGenerating meme post: {meme['name'][:50]}...")
        
        # Generate caption
        caption = self.generate_meme_caption(meme, meme['url'])
        
        if not caption:
            print("   Failed to generate caption")
            return None
        
        # Create post text with hashtags
        hashtags = self._generate_hashtags(meme)
        
        post_text = f"{caption}\n\n{hashtags}"
        
        # Validate post
        if len(post_text) > 2000:  # Facebook character limit
            post_text = f"{caption}\n\n#anime #meme"
        
        print(f"   Generated post: {post_text[:100]}...")
        
        return {
            "post_text": post_text,
            "image_url": meme['url'],
            "meme_id": meme['id'],
            "meme_name": meme['name'],
            "source": meme['source'],
            "post_type": "meme"
        }
    
    def _generate_hashtags(self, meme: Dict) -> str:
        """Generate relevant hashtags for meme."""
        base_hashtags = ["#anime", "#meme", "#animemes"]
        
        # Add source-specific hashtags
        source = meme.get('source', '')
        if source == 'imgflip':
            base_hashtags.append("#imgflip")
        elif source == 'meme_api':
            subreddit = meme.get('subreddit', '').lower()
            if 'animemes' in subreddit:
                base_hashtags.append("#animemes")
            elif 'anime' in subreddit:
                base_hashtags.append("#animecommunity")
        
        # Add random trending hashtags
        trending_tags = [
            "#otaku", "#weeb", "#kawaii", "#senpai", "#waifu",
            "#animeirl", "#animenocontext", "#wholesomeanimemes",
            "#animefan", "#mangafan", "#animecommunity"
        ]
        
        # Add 2-3 random trending tags
        additional_tags = random.sample(trending_tags, min(3, len(trending_tags)))
        
        all_tags = base_hashtags + additional_tags
        return " ".join(all_tags)
    
    def get_caption_ideas(self) -> list:
        """Get list of caption ideas for inspiration."""
        return [
            "When you finally understand the plot",
            "Me trying to explain anime to my parents",
            "That one character everyone loves",
            "When the anime ends but manga continues",
            "Anime logic be like",
            "This hits different at 3 AM",
            "Why is this so accurate",
            "Me watching anime instead of sleeping",
            "When the plot twist hits different",
            "Anime fans will understand"
        ]


# Global meme generator instance
_meme_generator = None

def get_meme_generator() -> MemeGenerator:
    """Get global meme generator instance."""
    global _meme_generator
    if _meme_generator is None:
        _meme_generator = MemeGenerator()
    return _meme_generator
