"""
Rate Limiter Utility
===================

Simple rate limiting implementation for API endpoints.
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Optional
from fastapi import HTTPException


class RateLimiter:
    """Simple rate limiter implementation."""
    
    def __init__(self):
        """Initialize rate limiter."""
        # Store request timestamps for each endpoint
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Rate limits per endpoint (requests per minute)
        self.limits = {
            "market_data": 60,      # 60 requests per minute
            "correlations": 30,     # 30 requests per minute
            "workflows": 10,        # 10 requests per minute
            "tasks": 20,           # 20 requests per minute
            "default": 100         # Default limit
        }
        
        # Time window in seconds
        self.window = 60
    
    async def check_rate_limit(self, endpoint: str, client_id: Optional[str] = None):
        """Check if request is within rate limits."""
        key = f"{endpoint}:{client_id}" if client_id else endpoint
        current_time = time.time()
        
        # Get request history for this key
        request_history = self.requests[key]
        
        # Remove old requests outside the time window
        while request_history and request_history[0] < current_time - self.window:
            request_history.popleft()
        
        # Check if within limits
        limit = self.limits.get(endpoint, self.limits["default"])
        if len(request_history) >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {limit} requests per minute for {endpoint}"
            )
        
        # Add current request
        request_history.append(current_time)
    
    def get_remaining_requests(self, endpoint: str, client_id: Optional[str] = None) -> int:
        """Get number of remaining requests for the current window."""
        key = f"{endpoint}:{client_id}" if client_id else endpoint
        current_time = time.time()
        
        # Get request history for this key
        request_history = self.requests[key]
        
        # Remove old requests outside the time window
        while request_history and request_history[0] < current_time - self.window:
            request_history.popleft()
        
        # Calculate remaining requests
        limit = self.limits.get(endpoint, self.limits["default"])
        return max(0, limit - len(request_history))
    
    def reset_limits(self, endpoint: Optional[str] = None, client_id: Optional[str] = None):
        """Reset rate limits for specific endpoint or client."""
        if endpoint and client_id:
            key = f"{endpoint}:{client_id}"
            if key in self.requests:
                self.requests[key].clear()
        elif endpoint:
            # Reset all limits for this endpoint
            keys_to_reset = [k for k in self.requests.keys() if k.startswith(f"{endpoint}:")]
            for key in keys_to_reset:
                self.requests[key].clear()
        else:
            # Reset all limits
            self.requests.clear() 