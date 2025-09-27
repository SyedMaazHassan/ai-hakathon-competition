#!/usr/bin/env python3
"""
Router Agent Service - Simple wrapper for the router agent
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from .agent import ROUTER_AGENT
from .pydantic_models import RouterInput, RouterDecision
from typing import Dict, Any, Optional


class RouterAgentService:
    """
    Simple service wrapper for the Router Agent.
    Takes a request text and city, returns router decision.
    """
    
    def __init__(self):
        """Initialize the router agent service"""
        self.router_agent = ROUTER_AGENT
    
    def route_request(
        self, 
        request_text: str, 
        user_city: Optional[str] = None,
        user_location: Optional[Dict[str, float]] = None
    ) -> RouterDecision:
        """
        Route a user request to the appropriate department.
        
        Args:
            request_text (str): User's emergency description
            user_city (str, optional): User's current city
            user_location (dict, optional): GPS coordinates {lat, lng}
            
        Returns:
            RouterDecision: Classification result with department, confidence, etc.
        """
        try:
            # Create input object
            input_data = RouterInput(
                request_text=request_text,
                user_city=user_city,
                user_location=user_location
            )
            
            # Call router agent
            result = self.router_agent.run(input=input_data)
            
            # Parse result
            if hasattr(result, 'content'):
                output = result.content
            else:
                output = result
            
            # Return the router decision
            return output
            
        except Exception as e:
            # Return a fallback decision in case of error
            return RouterDecision(
                department="municipal",  # Default fallback
                confidence=0.1,
                urgency_indicators=[],
                reason=f"Error processing request: {str(e)}",
                keywords_detected=[],
                degraded_mode_used=True,
                classification_source="fallback"
            )
    
    def route_request_simple(self, request_text: str, user_city: str = None) -> Dict[str, Any]:
        """
        Simplified version that returns a dictionary instead of Pydantic model.
        
        Args:
            request_text (str): User's emergency description
            user_city (str, optional): User's current city
            
        Returns:
            dict: Classification result as dictionary
        """
        decision = self.route_request(request_text, user_city)
        
        return {
            "department": decision.department,
            "confidence": decision.confidence,
            "urgency_indicators": decision.urgency_indicators,
            "reason": decision.reason,
            "keywords_detected": decision.keywords_detected,
            "degraded_mode_used": decision.degraded_mode_used,
            "classification_source": decision.classification_source
        }


# Create a singleton instance for easy import
router_service = RouterAgentService()


def route_emergency_request(request_text: str, user_city: str = None) -> Dict[str, Any]:
    """
    Convenience function to route an emergency request.
    
    Args:
        request_text (str): User's emergency description
        user_city (str, optional): User's current city
        
    Returns:
        dict: Classification result
    """
    return router_service.route_request_simple(request_text, user_city)
