"""
🎯 AI API WRAPPER
═══════════════════════════════════════════════════════════════
Simple wrapper functions for easy AI integration.
"""

from typing import Optional, Tuple
from .ai_client import MultiAIClient

# Global client instance
_ai_client = None


def initialize_ai_system() -> bool:
    """
    Initialize the multi-AI system. Call this at startup!
    Returns True if at least one model works.
    """
    global _ai_client
    
    print("\nInitializing Multi-AI System...")
    
    _ai_client = MultiAIClient()
    success = _ai_client.health_check_all_models()
    
    return success


def generate_text(prompt: str, task_type: str = "creative_writing",
                 temperature: float = 0.8) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate text with automatic model selection and fallback.
    
    Args:
        prompt: The prompt to send to AI
        task_type: Type of task (creative_writing, sentiment_analysis, etc.)
        temperature: Creativity level (0.0-1.0)
    
    Returns:
        (generated_text, model_name_used)
    """
    global _ai_client
    
    if not _ai_client:
        raise Exception("AI system not initialized! Call initialize_ai_system() first.")
    
    return _ai_client.generate_with_fallback(
        prompt=prompt,
        task_type=task_type,
        temperature=temperature
    )


def get_health_status() -> str:
    """Get current health status of all models."""
    global _ai_client
    
    if not _ai_client:
        return "AI system not initialized"
    
    return _ai_client.tracker.get_status_report()


def get_best_model_for_task(task_type: str) -> Optional[str]:
    """Get the current best model for a specific task."""
    global _ai_client
    
    if not _ai_client:
        return None
    
    suitable = _ai_client._get_suitable_models(task_type)
    return suitable[0] if suitable else None


def get_healthy_models() -> list:
    """Get list of currently healthy models."""
    global _ai_client
    
    if not _ai_client:
        return []
    
    return _ai_client.tracker.get_healthy_models()


def reset_model(model_name: str):
    """Reset a model's failure count for manual retry."""
    global _ai_client
    
    if _ai_client:
        _ai_client.tracker.reset_model(model_name)
