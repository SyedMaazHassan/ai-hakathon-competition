#!/usr/bin/env python3
"""
Simple Router Agent Test - Task 3 & 4
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.agents.router_agent.agent import ROUTER_AGENT
from apps.depts.agents.router_agent.pydantic_models import RouterInput
import json

def test_router_agent():
    """Test router agent with your exact I/O format"""

    print("🤖 TESTING ROUTER AGENT")
    print("=" * 40)

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

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: {test_input['request_text'][:50]}...")
        print(f"   City: {test_input['user_city']}")
        print("-" * 30)

        try:
            test_input = RouterInput(
                request_text=test_input['request_text'], 
                user_city=test_input['user_city']
            )
            # Call router agent
            result = ROUTER_AGENT.run(input=test_input)

            # Parse result
            if hasattr(result, 'content'):
                output = result.content
            else:
                output = result

            # Print in your desired format
            print(f"✅ Output:")
            print(output)
            # print(f"   category: {output.get('department', 'unknown')}")
            # print(f"   confidence: {output.get('confidence', 0.0):.2f}")
            # print(f"   rationale: {output.get('reason', 'No reason')[:60]}...")

            # # Additional details
            # print(f"   degraded_mode: {output.get('degraded_mode_used', False)}")
            # print(f"   keywords: {output.get('keywords_detected', [])}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_router_agent()