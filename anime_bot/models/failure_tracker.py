"""
FAILURE TRACKER
═══════════════════════════════════════════════════════════════
Persistent failure tracking and logging system.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

from anime_bot.config import FAILURE_TRACKER_FILE


class FailureTracker:
    """Track persistent failures across bot restarts."""
    
    def __init__(self):
        self.file_path = FAILURE_TRACKER_FILE
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load failure data from JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading failure tracker: {e}")
                return self._create_empty_data()
        else:
            return self._create_empty_data()
    
    def _create_empty_data(self) -> Dict[str, Any]:
        """Create empty failure data structure."""
        return {
            "total_failures": 0,
            "failure_log": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_data(self) -> bool:
        """Save failure data to JSON file."""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving failure tracker: {e}")
            return False
    
    def increment_failure_counter(self) -> int:
        """Increment total failure counter and return new count."""
        self.data["total_failures"] += 1
        self._save_data()
        return self.data["total_failures"]
    
    def get_failure_count(self) -> int:
        """Get current total failure count."""
        return self.data["total_failures"]
    
    def log_failure(self, error_type: str, details: str, retry_count: int = 0) -> None:
        """Log a failure with details."""
        failure_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "details": details,
            "retry_count": retry_count
        }
        
        self.data["failure_log"].append(failure_entry)
        
        # Keep only last 100 failures to prevent file from growing too large
        if len(self.data["failure_log"]) > 100:
            self.data["failure_log"] = self.data["failure_log"][-100:]
        
        self._save_data()
    
    def calculate_retry_delay(self, attempt: int) -> int:
        """Calculate exponential backoff delay."""
        from anime_bot.config import RETRY_BASE_DELAY, RETRY_MAX_DELAY
        
        delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
        return min(delay, RETRY_MAX_DELAY)
    
    def get_failure_stats(self) -> Dict[str, Any]:
        """Get failure statistics."""
        recent_failures = [
            f for f in self.data["failure_log"]
            if datetime.fromisoformat(f["timestamp"]).date() == datetime.now().date()
        ]
        
        failure_types = {}
        for failure in self.data["failure_log"]:
            error_type = failure["type"]
            failure_types[error_type] = failure_types.get(error_type, 0) + 1
        
        return {
            "total_failures": self.data["total_failures"],
            "today_failures": len(recent_failures),
            "failure_types": failure_types,
            "last_failure": self.data["failure_log"][-1] if self.data["failure_log"] else None,
            "last_updated": self.data["last_updated"]
        }
    
    def get_recent_failures(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failures from last N hours."""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        recent = []
        for failure in self.data["failure_log"]:
            failure_time = datetime.fromisoformat(failure["timestamp"]).timestamp()
            if failure_time >= cutoff_time:
                recent.append(failure)
        
        return recent
    
    def clear_old_failures(self, days: int = 7) -> int:
        """Clear failures older than N days."""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        original_count = len(self.data["failure_log"])
        
        self.data["failure_log"] = [
            f for f in self.data["failure_log"]
            if datetime.fromisoformat(f["timestamp"]).timestamp() >= cutoff_time
        ]
        
        removed_count = original_count - len(self.data["failure_log"])
        if removed_count > 0:
            self._save_data()
        
        return removed_count


# Global failure tracker instance
_failure_tracker = None

def get_failure_tracker() -> FailureTracker:
    """Get global failure tracker instance."""
    global _failure_tracker
    if _failure_tracker is None:
        _failure_tracker = FailureTracker()
    return _failure_tracker
