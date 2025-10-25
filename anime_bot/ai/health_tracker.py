"""
🏥 MODEL HEALTH TRACKER
═══════════════════════════════════════════════════════════════
Tracks which models are working and their performance.
"""

from datetime import datetime
from typing import List, Dict
from .model_config import AI_MODELS


class ModelHealthTracker:
    """Tracks which models are working and their performance."""
    
    def __init__(self):
        self.health_status = {}
        self.performance_stats = {}
        self.last_check = None
        
        for model_name in AI_MODELS.keys():
            self.health_status[model_name] = {
                "is_healthy": None,  # None = not tested, True = working, False = failed
                "last_success": None,
                "last_failure": None,
                "consecutive_failures": 0,
                "total_calls": 0,
                "total_successes": 0,
                "total_failures": 0,
                "avg_response_time": 0
            }
    
    def mark_success(self, model_name: str, response_time: float):
        """Mark a successful API call."""
        status = self.health_status[model_name]
        status["is_healthy"] = True
        status["last_success"] = datetime.now().isoformat()
        status["consecutive_failures"] = 0
        status["total_calls"] += 1
        status["total_successes"] += 1
        
        # Update average response time
        total = status["total_successes"]
        current_avg = status["avg_response_time"]
        status["avg_response_time"] = (current_avg * (total - 1) + response_time) / total
    
    def mark_failure(self, model_name: str, error: str):
        """Mark a failed API call."""
        status = self.health_status[model_name]
        status["is_healthy"] = False
        status["last_failure"] = datetime.now().isoformat()
        status["consecutive_failures"] += 1
        status["total_calls"] += 1
        status["total_failures"] += 1
    
    def get_healthy_models(self, tier: int = None) -> List[str]:
        """Get list of healthy models, optionally filtered by tier."""
        healthy = []
        
        for model_name, status in self.health_status.items():
            # Skip if not healthy (and has been tested)
            if status["is_healthy"] == False:
                continue
            
            # Skip if too many consecutive failures (even if not recently tested)
            if status["consecutive_failures"] >= 3:
                continue
            
            # Filter by tier if specified
            if tier and AI_MODELS[model_name]["tier"] != tier:
                continue
            
            healthy.append(model_name)
        
        # Sort by success rate and speed
        healthy.sort(key=lambda x: (
            self.health_status[x]["total_successes"] / max(self.health_status[x]["total_calls"], 1),
            -AI_MODELS[x]["tier"],
            self.health_status[x]["avg_response_time"]
        ), reverse=True)
        
        return healthy
    
    def get_status_report(self) -> str:
        """Generate a human-readable status report."""
        lines = ["\n" + "="*70]
        lines.append("AI MODEL HEALTH STATUS")
        lines.append("="*70)
        
        for tier in [1, 2, 3]:
            tier_models = [m for m, info in AI_MODELS.items() if info["tier"] == tier]
            if not tier_models:
                continue
                
            lines.append(f"\nTIER {tier} MODELS:")
            
            for model_name in tier_models:
                status = self.health_status[model_name]
                info = AI_MODELS[model_name]
                
                # Status icon
                if status["is_healthy"] == None:
                    icon = "O"
                    health_text = "NOT TESTED"
                elif status["is_healthy"]:
                    icon = "OK"
                    health_text = "HEALTHY"
                else:
                    icon = "X"
                    health_text = "FAILED"
                
                # Success rate
                total = status["total_calls"]
                if total > 0:
                    success_rate = (status["total_successes"] / total) * 100
                    rate_text = f"{success_rate:.0f}% success"
                else:
                    rate_text = "No calls yet"
                
                # Response time
                if status["avg_response_time"] > 0:
                    time_text = f"{status['avg_response_time']:.2f}s avg"
                else:
                    time_text = ""
                
                lines.append(f"   {icon} {model_name:20} | {health_text:12} | {rate_text:15} | {time_text}")
        
        lines.append("="*70 + "\n")
        return "\n".join(lines)
    
    def get_model_stats(self, model_name: str) -> Dict:
        """Get detailed stats for a specific model."""
        return self.health_status.get(model_name, {})
    
    def reset_model(self, model_name: str):
        """Reset a model's failure count (for manual retry)."""
        if model_name in self.health_status:
            self.health_status[model_name]["consecutive_failures"] = 0
            self.health_status[model_name]["is_healthy"] = None
