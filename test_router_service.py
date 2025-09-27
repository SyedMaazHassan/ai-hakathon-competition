#!/usr/bin/env python3
"""
Test Router Agent Service
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.agents.router_agent.service import RouterAgentService, route_emergency_request
import json

def test_router_service():
    """Test the router agent service"""
    
    print("🤖 TESTING ROUTER AGENT SERVICE")
    print("=" * 50)
    
    # Initialize service
    service = RouterAgentService()
    
    test_cases = [
        {
            "request_text": "My father is having chest pain and cannot breathe",
            "user_city": "Lahore"
        },
        {
            "request_text": "There's a fire in my building, people are trapped",
            "user_city": "Karachi"
        },
        {
            "request_text": "Someone broke into my house and stole everything",
            "user_city": "Islamabad"
        },
        {
            "request_text": "میرے والد کو دل کا دورہ پڑا ہے",  # Urdu
            "user_city": "Lahore"
        }
    ]
    
    print("\n1. Testing RouterAgentService class:")
    print("-" * 40)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: {test_input['request_text'][:50]}...")
        print(f"   City: {test_input['user_city']}")
        
        try:
            # Test the service method
            result = service.route_request_simple(
                request_text=test_input['request_text'],
                user_city=test_input['user_city']
            )
            
            print(f"✅ Output:")
            print(f"   Department: {result['department']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Reason: {result['reason'][:60]}...")
            print(f"   Keywords: {result['keywords_detected']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n\n2. Testing convenience function:")
    print("-" * 40)
    
    # Test the convenience function
    test_input = test_cases[0]
    try:
        result = route_emergency_request(
            request_text=test_input['request_text'],
            user_city=test_input['user_city']
        )
        
        print(f"Input: {test_input['request_text']}")
        print(f"City: {test_input['user_city']}")
        print(f"✅ Output: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_router_service()
