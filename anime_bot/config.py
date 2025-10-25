"""
🔑 CONFIGURATION
═══════════════════════════════════════════════════════════════
All API keys, settings, and constants for the anime news bot.
"""

# ═══════════════════════════════════════════════════════════════
# 🔑 API KEYS
# ═══════════════════════════════════════════════════════════════

# OpenRouter API Key (for multiple AI models)
OPENROUTER_API_KEY = "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"

# Gemini API Key (direct backup)
GEMINI_API_KEY = "AIzaSyBuhTmFyDbiODATAfSonV6OHvHp7K--4B8"

# Facebook Page Token
FACEBOOK_PAGE_TOKEN = "EAAVvytv2lLMBP0NLZBdJ3bGNZB7dZBDgvpzGfkhDGNtvDbV5ZAVFhs0CSgrx7qLmmDTyPiRblL8ecBSdGH5Iv1sxgZB9Y8UwmesSNn6eOmdZBXZBnDBciQvbuJMl0ViCCkGADRruFrYirxZB6wvrcVEBzN0dUX9w8dVBZBKiIEcttnZB9AeTF3CMvby3GLqLtmY9CxgykKZAMt0XjNCTkCFlxzAxZCaL"

# Optional: For OpenRouter rankings
YOUR_SITE_URL = "https://anime-news-bot.example.com"
YOUR_SITE_NAME = "Anime News Bot"

# ═══════════════════════════════════════════════════════════════
# 📰 NEWS SOURCES
# ═══════════════════════════════════════════════════════════════

ANIME_NEWS_SOURCES = [
    "https://www.animenewsnetwork.com/all/rss.xml",    # 156 entries - All anime news
    "https://myanimelist.net/rss/news.xml",           # 20 entries - MAL news
    "https://www.animenewsnetwork.com/news/rss.xml"   # 40 entries - ANN news only
]

# ═══════════════════════════════════════════════════════════════
# ⚙️ SETTINGS
# ═══════════════════════════════════════════════════════════════

# Article quality threshold (0-10)
MIN_ARTICLE_QUALITY_SCORE = 6

# Maximum posts per day
MAX_POSTS_PER_DAY = 1

# Database file path
DATABASE_FILE = "anime_news_database.json"

# ═══════════════════════════════════════════════════════════════
# 🤖 AI MODEL SETTINGS
# ═══════════════════════════════════════════════════════════════

# Default temperature for AI generation
DEFAULT_TEMPERATURE = 0.8

# Maximum tokens for AI responses
MAX_TOKENS = 600

# Maximum attempts per model before fallback
MAX_ATTEMPTS_PER_MODEL = 2

# ═══════════════════════════════════════════════════════════════
# 📊 QUALITY SCORING WEIGHTS
# ═══════════════════════════════════════════════════════════════

# Trending keywords that boost article quality
TRENDING_KEYWORDS = {
    "season 2": 2.0, "season 3": 2.0, "announcement": 1.5,
    "trailer": 1.7, "premiere": 1.6, "confirmed": 1.5,
    "adaptation": 2.0, "movie": 1.8
}

# Boring keywords that reduce article quality
BORING_KEYWORDS = {
    "merchandise": -2.0, "figure": -1.5, "cafe": -2.0
}

# ═══════════════════════════════════════════════════════════════
# 🎯 ANIME RELEVANCE CHECK
# ═══════════════════════════════════════════════════════════════

# Fallback keywords for anime relevance check
ANIME_KEYWORDS = [
    'anime', 'season', 'episode', 'adaptation', 
    'studio', 'voice actor'
]

# Minimum confidence for anime relevance (0.0-1.0)
MIN_ANIME_CONFIDENCE = 0.5

# ═══════════════════════════════════════════════════════════════
# 📤 FACEBOOK SETTINGS
# ═══════════════════════════════════════════════════════════════

# Facebook Graph API endpoint
FACEBOOK_API_URL = "https://graph.facebook.com/me/feed"

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# ═══════════════════════════════════════════════════════════════
# ⏰ TIMING SETTINGS
# ═══════════════════════════════════════════════════════════════

# Delay between posts (seconds)
POST_DELAY = 5

# Health check delay between models (seconds)
HEALTH_CHECK_DELAY = 1

# Retry delay for failed models (seconds)
RETRY_DELAY = 2

# ═══════════════════════════════════════════════════════════════
# 🎯 DIVERSITY & FRESHNESS SETTINGS
# ═══════════════════════════════════════════════════════════════

# Minimum similarity threshold for diversity (0.0-1.0)
MIN_SIMILARITY_THRESHOLD = 0.7

# Boost score for fresh content (hours)
FRESHNESS_BOOST_HOURS = 24

# Emotional engagement bonus multiplier
EMOTIONAL_ENGAGEMENT_BONUS = 1.5

# Variety in post styles (random selection)
USE_RANDOM_POST_STYLES = True

# ═══════════════════════════════════════════════════════════════
# 🖼️ IMAGE SETTINGS
# ═══════════════════════════════════════════════════════════════

# Enable image attachments
ENABLE_IMAGE_ATTACHMENTS = True

# Image extraction priority order
IMAGE_EXTRACTION_PRIORITY = ["article", "cover_art", "fallback_api"]

# Fallback image APIs
FALLBACK_IMAGE_APIS = [
    "https://api.waifu.pics/sfw/waifu",
    "https://nekos.best/api/v2/neko"
]

# Image quality settings
IMAGE_QUALITY_CHECK = True
MAX_IMAGE_SIZE_MB = 5

# Free anime image APIs
MAL_API_BASE = "https://api.jikan.moe/v4"
ANILIST_API_URL = "https://graphql.anilist.co"

# Random scheduling settings
MIN_POST_HOUR = 9  # 9 AM
MAX_POST_HOUR = 21  # 9 PM

# ═══════════════════════════════════════════════════════════════
# 🔗 WEBHOOK CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Discord webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1431650773426634832/WU3UWjEknGiv34EU5c64A4UYZdJpFPt9nhOGcEGNTpvpHZ9Qkxw_Kko4UWp_KN6Vqx3b"

# ═══════════════════════════════════════════════════════════════
# 🎭 MEME SETTINGS
# ═══════════════════════════════════════════════════════════════

# Meme posting settings
MIN_MEMES_PER_DAY = 3
MAX_MEMES_PER_DAY = 5

# Free meme API URLs
MEME_API_URLS = [
    "https://meme-api.com/gimme/animemes",
    "https://meme-api.com/gimme/Animemes"
]

# ═══════════════════════════════════════════════════════════════
# 🔄 RETRY & RECOVERY SETTINGS
# ═══════════════════════════════════════════════════════════════

# Retry configuration
MAX_RETRY_ATTEMPTS = 5
RETRY_BASE_DELAY = 1  # seconds
RETRY_MAX_DELAY = 32  # seconds

# Failure tracking
FAILURE_TRACKER_FILE = "failure_tracker.json"

# Continuous operation
ENABLE_CONTINUOUS_MODE = True
SCHEDULE_CHECK_INTERVAL = 60  # seconds
