#!/usr/bin/env python3
"""
Test Department Agent End-to-End - Task 8
Tests the complete workflow: Router -> Department Agent -> Action Plan
"""
import os
import sys
import django
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

from apps.depts.agents.router_agent.service import router_service
from apps.depts.agents.router_agent.pydantic_models import RouterDecision
from apps.depts.agents.department_agent.service import process_citizen_request
import json

def test_department_agent():
    """Test Department Agent with Router Agent output"""

    print("🏥 TESTING DEPARTMENT AGENT - END-TO-END")
    print("=" * 50)

    test_cases = [
        {
            "name": "Health Emergency - Chest Pain",
            "request_text": "My father is having chest pain and cannot breathe",
            "user_city": "Lahore",
            "user_location": None
        },
        {
            "name": "Fire Emergency - Building Fire",
            "request_text": "There's a fire in my building, people are trapped on 3rd floor",
            "user_city": "Karachi",
            "user_location": {"lat": 24.8607, "lng": 67.0011}
        },
        {
            "name": "Police Emergency - Robbery",
            "request_text": "Someone broke into my house and stole everything",
            "user_city": "Islamabad",
            "user_location": None
        },
        {
            "name": "Urdu Request - Health",
            "request_text": "میرے والد کو دل کا دورہ پڑا ہے، سانس نہیں آ رہی",
            "user_city": "Lahore",
            "user_location": None
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        print(f"📝 Request: {test_case['request_text']}")
        print(f"🌍 City: {test_case['user_city']}")
        if test_case['user_location']:
            print(f"📍 Location: {test_case['user_location']}")

        try:
            # Step 1: Run Router Agent Service
            print("\n🤖 STEP 1: Router Agent Classification")
            router_decision = router_service.route_request(
                request_text=test_case['request_text'],
                user_city=test_case['user_city'],
                user_location=test_case['user_location']
            )

            print(f"🎯 Department: {router_decision.department}")
            print(f"📊 Confidence: {router_decision.confidence:.2f}")
            print(f"🚨 Urgency Indicators: {router_decision.urgency_indicators}")

            # Step 2: Run Department Agent
            print("\n🏥 STEP 2: Department Agent Processing")
            dept_result = process_citizen_request(
                router_decision=router_decision,
                user_city=test_case['user_city'],
                user_location=test_case['user_location']
            )

            if dept_result.success:
                print(f"✅ Success: {dept_result.success}")
                print(f"🚨 Urgency Level: {dept_result.urgency}")
                print(f"🏢 Assigned Entity: {dept_result.assigned_entity.name}")
                print(f"📞 Contact: {dept_result.assigned_entity.phone}")
                print(f"🏙️ Location: {dept_result.assigned_entity.city}")
                print(f"📍 Match Reason: {dept_result.assigned_entity.match_reason}")

                # Action Plan Details
                print(f"\n📋 ACTION PLAN")
                print(f"⏱️ Estimated Resolution: {dept_result.action_plan.estimated_resolution_time}")

                print(f"\n🚨 IMMEDIATE ACTIONS:")
                for action in dept_result.action_plan.immediate_actions:
                    print(f"  {action.step_number}. {action.action}")
                    print(f"     ⏰ Timeline: {action.timeline}")
                    print(f"     👤 Responsible: {action.responsible_party}")

                print(f"\n🔄 FOLLOW-UP ACTIONS:")
                for action in dept_result.action_plan.follow_up_actions:
                    print(f"  {action.step_number}. {action.action}")
                    print(f"     ⏰ Timeline: {action.timeline}")
                    print(f"     👤 Responsible: {action.responsible_party}")

                print(f"\n💭 RATIONALE:")
                print(f"{dept_result.rationale}")

            else:
                print(f"❌ Error: {dept_result.error_message}")

        except Exception as e:
            print(f"💥 Exception: {str(e)}")

def test_urgency_assessment():
    """Test urgency assessment logic"""
    print("\n" + "=" * 50)
    print("🚨 TESTING URGENCY ASSESSMENT")
    print("=" * 50)

    from apps.depts.agents.department_agent.service import DepartmentAgentService

    test_decisions = [
        {
            "name": "Critical - Heart Attack",
            "decision": RouterDecision(
                department="health",
                confidence=0.95,
                urgency_indicators=["chest pain", "breathing difficulty"],
                reason="Medical emergency",
                keywords_detected=["heart attack", "cardiac"]
            ),
            "expected": "critical"
        },
        {
            "name": "High - Robbery",
            "decision": RouterDecision(
                department="police",
                confidence=0.88,
                urgency_indicators=["theft", "robbery"],
                reason="Crime reported",
                keywords_detected=["broke", "stole"]
            ),
            "expected": "high"
        },
        {
            "name": "Medium - High Confidence",
            "decision": RouterDecision(
                department="municipal",
                confidence=0.85,
                urgency_indicators=["complaint"],
                reason="Service request",
                keywords_detected=["water", "supply"]
            ),
            "expected": "medium"
        }
    ]

    for test in test_decisions:
        urgency = DepartmentAgentService.assess_urgency(test["decision"])
        status = "✅" if urgency == test["expected"] else "❌"
        print(f"{status} {test['name']}: {urgency} (expected: {test['expected']})")

if __name__ == "__main__":
    test_department_agent()
    test_urgency_assessment()