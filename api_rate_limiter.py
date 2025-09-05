"""
API Rate Limiter Module
Manages API call frequency to avoid hitting rate limits
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class APIRateLimiter:
    """Manages API rate limiting with configurable limits"""
    
    def __init__(self, max_calls_per_hour: int = 5, rate_file: str = 'api_rate_limit.json'):
        self.max_calls_per_hour = max_calls_per_hour
        self.rate_file = rate_file
        self.call_history = self._load_call_history()
    
    def _load_call_history(self) -> Dict:
        """Load call history from file"""
        try:
            if os.path.exists(self.rate_file):
                with open(self.rate_file, 'r') as f:
                    data = json.load(f)
                    # Clean old entries (older than 1 hour)
                    cutoff_time = datetime.now() - timedelta(hours=1)
                    data['calls'] = [
                        call for call in data.get('calls', [])
                        if datetime.fromisoformat(call) > cutoff_time
                    ]
                    return data
        except Exception as e:
            logger.warning(f"Could not load rate limit history: {e}")
        
        return {'calls': []}
    
    def _save_call_history(self):
        """Save call history to file"""
        try:
            with open(self.rate_file, 'w') as f:
                json.dump(self.call_history, f, default=str)
        except Exception as e:
            logger.error(f"Could not save rate limit history: {e}")
    
    def can_make_call(self) -> bool:
        """Check if we can make an API call without exceeding rate limit"""
        # Clean old entries
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.call_history['calls'] = [
            call for call in self.call_history.get('calls', [])
            if datetime.fromisoformat(call) > cutoff_time
        ]
        
        current_calls = len(self.call_history['calls'])
        can_call = current_calls < self.max_calls_per_hour
        
        if not can_call:
            oldest_call = min(self.call_history['calls'])
            next_available = datetime.fromisoformat(oldest_call) + timedelta(hours=1)
            logger.info(f"Rate limit reached ({current_calls}/{self.max_calls_per_hour}). Next call available at: {next_available}")
        
        return can_call
    
    def record_call(self):
        """Record that an API call was made"""
        now = datetime.now()
        self.call_history['calls'].append(now.isoformat())
        self._save_call_history()
        logger.info(f"API call recorded. Total calls in last hour: {len(self.call_history['calls'])}")
    
    def get_next_available_time(self) -> Optional[datetime]:
        """Get the next time when an API call can be made"""
        if self.can_make_call():
            return None
        
        if not self.call_history['calls']:
            return None
        
        oldest_call = min(self.call_history['calls'])
        return datetime.fromisoformat(oldest_call) + timedelta(hours=1)
    
    def get_calls_remaining(self) -> int:
        """Get number of calls remaining in current hour"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.call_history['calls'] = [
            call for call in self.call_history.get('calls', [])
            if datetime.fromisoformat(call) > cutoff_time
        ]
        
        current_calls = len(self.call_history['calls'])
        return max(0, self.max_calls_per_hour - current_calls)

# Global rate limiter instance
api_rate_limiter = APIRateLimiter(max_calls_per_hour=5)

def check_api_rate_limit() -> bool:
    """Check if we can make an API call"""
    return api_rate_limiter.can_make_call()

def record_api_call():
    """Record that an API call was made"""
    api_rate_limiter.record_call()

def get_api_calls_remaining() -> int:
    """Get remaining API calls in current hour"""
    return api_rate_limiter.get_calls_remaining()

def get_next_api_call_time() -> Optional[datetime]:
    """Get next available time for API call"""
    return api_rate_limiter.get_next_available_time()

if __name__ == "__main__":
    # Test rate limiter
    limiter = APIRateLimiter(max_calls_per_hour=3)  # Lower limit for testing
    
    print(f"Can make call: {limiter.can_make_call()}")
    print(f"Calls remaining: {limiter.get_calls_remaining()}")
    
    # Simulate making calls
    for i in range(5):
        if limiter.can_make_call():
            limiter.record_call()
            print(f"Call {i+1} made. Remaining: {limiter.get_calls_remaining()}")
        else:
            next_time = limiter.get_next_available_time()
            print(f"Call {i+1} blocked. Next available: {next_time}")
