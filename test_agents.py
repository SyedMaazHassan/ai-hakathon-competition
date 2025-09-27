#!/usr/bin/env python3
"""
Quick test script for AI agents - No frontend needed!
Run: python test_agents.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

# Import your models and agents
from apps.depts.models import CitizenRequest, Department, DepartmentEntity
from router_agent.agent import ROUTER_AGENT

def test_router_agent():
    """Test router agent with sample requests"""

    test_cases = [
        "My father is having chest pain and difficulty breathing",
        "There's a fire in my building, people are trapped",
        "Someone broke into my house and stole everything",
        "I need to get my birth certificate from government office",
        "Car accident on Highway 5, people are injured",
        "میرے والد کو دل کا دورہ پڑا ہے",  # Urdu: My father is having heart attack
    ]

    print("🤖 TESTING ROUTER AGENT")
    print("=" * 50)

    for i, request_text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{request_text}'")
        print("-" * 30)

        try:
            # Test your router agent
            result = ROUTER_AGENT.run(request_text)

            # Print results
            print(f"✅ Category: {result.get('category', 'Unknown')}")
            print(f"⚡ Urgency: {result.get('urgency', 'Unknown')}")
            print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
            print(f"🧠 Reasoning: {result.get('reasoning', 'No reasoning')}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_database_integration():
    """Test creating records in database"""
    print("\n\n📊 TESTING DATABASE INTEGRATION")
    print("=" * 50)

    try:
        # Test creating a citizen request
        request = CitizenRequest.objects.create(
            request_text="Test emergency request",
            category="HEALTH",
            urgency_level="HIGH",
            confidence_score=0.95,
            ai_response="Test AI response"
        )

        print(f"✅ Created request: {request.case_code}")
        print(f"📝 Text: {request.request_text}")
        print(f"🏥 Category: {request.category}")

        # Clean up
        request.delete()
        print("🧹 Cleaned up test data")

    except Exception as e:
        print(f"❌ Database Error: {str(e)}")

def test_available_departments():
    """Show available departments for routing"""
    print("\n\n🏛️ AVAILABLE DEPARTMENTS")
    print("=" * 50)

    departments = Department.objects.filter(is_active=True)

    for dept in departments:
        print(f"🏢 {dept.name}")
        print(f"   Category: {dept.category}")
        print(f"   24x7: {'Yes' if dept.is_24x7 else 'No'}")
        print(f"   Entities: {dept.entities.count()}")
        print()

if __name__ == "__main__":
    print("🚀 EMERGENCY SERVICES AI - AGENT TESTING")
    print("=" * 60)

    # Run tests
    test_router_agent()
    test_database_integration()
    test_available_departments()

    print("\n✅ All tests completed!")
    print("💡 Tip: Modify test_cases in test_router_agent() to test more scenarios")