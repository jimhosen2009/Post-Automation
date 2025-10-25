"""
🤖 MODEL CONFIGURATION
═══════════════════════════════════════════════════════════════
AI model definitions and capabilities.
"""

# ═══════════════════════════════════════════════════════════════
# 🤖 MODEL CONFIGURATION (Based on Research)
# ═══════════════════════════════════════════════════════════════

AI_MODELS = {
    # Tier 1: BEST QUALITY (Try these first)
    "gemini-2.0-flash": {
        "id": "google/gemini-2.0-flash-exp:free",
        "provider": "openrouter",
        "tier": 1,
        "speed": "very_fast",
        "creativity": 9,
        "instruction_following": 9,
        "context_length": 32768,
        "multimodal": True,
        "best_for": ["creative_writing", "sentiment_analysis", "image_analysis"],
        "notes": "Latest Google model, excellent at social media posts"
    },
    
    "llama-3.3-70b": {
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "provider": "openrouter",
        "tier": 1,
        "speed": "fast",
        "creativity": 8,
        "instruction_following": 10,
        "context_length": 131072,
        "multimodal": False,
        "best_for": ["instruction_following", "consistent_output", "long_context"],
        "notes": "70B model, very reliable, great at following prompts precisely"
    },
    
    "qwen-2.5-72b": {
        "id": "qwen/qwen-2.5-72b-instruct:free",
        "provider": "openrouter",
        "tier": 1,
        "speed": "fast",
        "creativity": 8,
        "instruction_following": 9,
        "context_length": 32768,
        "multimodal": False,
        "best_for": ["reasoning", "multilingual", "quality_check"],
        "notes": "72B model, excellent for Japanese/English content"
    },
    
    # Tier 2: GOOD BACKUP (Reliable fallbacks)
    "llama-3.1-8b": {
        "id": "meta-llama/llama-3.1-8b-instruct",
        "provider": "openrouter",
        "tier": 2,
        "speed": "fast",
        "creativity": 7,
        "instruction_following": 8,
        "context_length": 131072,
        "multimodal": False,
        "best_for": ["reasoning", "analysis", "quick_tasks"],
        "notes": "Fast 8B model, good backup for reasoning tasks"
    },
    
    "hermes-3-405b": {
        "id": "nousresearch/hermes-3-llama-3.1-405b:free",
        "provider": "openrouter",
        "tier": 2,
        "speed": "slow",
        "creativity": 9,
        "instruction_following": 8,
        "context_length": 131072,
        "multimodal": False,
        "best_for": ["creative_writing", "roleplay"],
        "notes": "405B model! Very creative but slow"
    },
    
    # Tier 3: LIGHTWEIGHT (Fast but less powerful)
    "mistral-nemo": {
        "id": "mistralai/mistral-nemo:free",
        "provider": "openrouter",
        "tier": 3,
        "speed": "very_fast",
        "creativity": 7,
        "instruction_following": 7,
        "context_length": 131072,
        "multimodal": False,
        "best_for": ["quick_tasks", "speed"],
        "notes": "Fast and efficient, good for simple tasks"
    },
    
    # DIRECT GEMINI (Outside OpenRouter - separate quota!)
    "gemini-direct": {
        "id": "gemini-2.0-flash-exp",
        "provider": "gemini_direct",
        "tier": 1,
        "speed": "very_fast",
        "creativity": 9,
        "instruction_following": 9,
        "context_length": 1000000,
        "multimodal": True,
        "best_for": ["creative_writing", "long_context"],
        "notes": "Direct Gemini API - separate quota from OpenRouter!"
    }
}
