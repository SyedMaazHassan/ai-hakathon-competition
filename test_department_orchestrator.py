#!/usr/bin/env python3
"""
Test Department Orchestrator Agent - Isolated Service Testing
Tests only the Department Orchestrator service with specialized agents
"""
import os
import sys
import django
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.agents.router_agent.pydantic_models import RouterDecision
from apps.depts.agents.department_orchestrator_agent.service import process_department_request
from apps.depts.agents.department_orchestrator_agent.pydantic_models import DepartmentOrchestratorInput
from apps.depts.choices import DepartmentCategory

def test_department_orchestrator():
    """Test Department Orchestrator with different emergency scenarios"""

    print("🏛️ TESTING DEPARTMENT ORCHESTRATOR AGENT")
    print("=" * 50)

    test_scenarios = [
        {
            "name": "Police Emergency - Robbery",
            "original_request": "Someone broke into my house and stole everything",
            "user_city": "Lahore",
            "router_decision": RouterDecision(
                department=DepartmentCategory.POLICE,
                confidence=0.92,
                urgency_indicators=["theft", "robbery", "emergency"],
                reason="Crime reported - theft and burglary",
                keywords_detected=["broke", "stole", "house"],
                degraded_mode_used=False,
                classification_source="llm"
            )
        },
        {
            "name": "Fire Emergency - Building Fire",
            "original_request": "There's a fire in my building, people are trapped",
            "user_city": "Karachi",
            "router_decision": RouterDecision(
                department=DepartmentCategory.FIRE_BRIGADE,
                confidence=0.95,
                urgency_indicators=["fire", "trapped", "emergency"],
                reason="Fire emergency with people at risk",
                keywords_detected=["fire", "building", "trapped"],
                degraded_mode_used=False,
                classification_source="llm"
            )
        },
        {
            "name": "Medical Emergency - Heart Attack",
            "original_request": "My father is having chest pain and cannot breathe",
            "user_city": "Islamabad",
            "router_decision": RouterDecision(
                department=DepartmentCategory.AMBULANCE,
                confidence=0.90,
                urgency_indicators=["chest pain", "breathing difficulty", "medical emergency"],
                reason="Medical emergency - possible cardiac event",
                keywords_detected=["chest pain", "breathe", "father"],
                degraded_mode_used=False,
                classification_source="llm"
            )
        },
        {
            "name": "Cybercrime - Account Hacking",
            "original_request": "Someone hacked my bank account and transferred money",
            "user_city": "Lahore",
            "router_decision": RouterDecision(
                department=DepartmentCategory.CYBERCRIME,
                confidence=0.88,
                urgency_indicators=["hacked", "financial fraud", "unauthorized access"],
                reason="Cybercrime - financial fraud and unauthorized access",
                keywords_detected=["hacked", "bank account", "transferred money"],
                degraded_mode_used=False,
                classification_source="llm"
            )
        },
        {
            "name": "Disaster Emergency - Earthquake",
            "original_request": "Strong earthquake hit our area, buildings are damaged",
            "user_city": "Quetta",
            "router_decision": RouterDecision(
                department=DepartmentCategory.DISASTER_MGMT,
                confidence=0.93,
                urgency_indicators=["earthquake", "building damage", "natural disaster"],
                reason="Natural disaster - earthquake with structural damage",
                keywords_detected=["earthquake", "buildings", "damaged"],
                degraded_mode_used=False,
                classification_source="llm"
            )
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 40)
        print(f"📝 Request: {scenario['original_request']}")
        print(f"🌍 City: {scenario['user_city']}")
        print(f"🎯 Department: {scenario['router_decision'].department}")
        print(f"📊 Confidence: {scenario['router_decision'].confidence:.2f}")

        try:
            # Test the Department Orchestrator service
            result = process_department_request(
                original_request=scenario['original_request'],
                router_decision=scenario['router_decision'],
                user_city=scenario['user_city'],
                user_location=None
            )

            if result.success:
                print(f"\n✅ SUCCESS!")
                print(f"🚨 Criticality: {result.criticality}")
                print(f"💭 Rationale: {result.rationale[:100]}...")

                if result.action_plan:
                    print(f"\n📋 ACTION PLAN:")
                    print(f"⏱️ Resolution Time: {result.action_plan.estimated_resolution_time}")

                    print(f"\n🚨 IMMEDIATE ACTIONS ({len(result.action_plan.immediate_actions)}):")
                    for action in result.action_plan.immediate_actions[:3]:  # Show first 3
                        print(f"  {action.step_number}. {action.action[:60]}...")
                        print(f"     ⏰ {action.timeline} | 👤 {action.responsible_party}")

                    print(f"\n🔄 FOLLOW-UP ACTIONS ({len(result.action_plan.follow_up_actions)}):")
                    for action in result.action_plan.follow_up_actions[:2]:  # Show first 2
                        print(f"  {action.step_number}. {action.action[:60]}...")
                        print(f"     ⏰ {action.timeline} | 👤 {action.responsible_party}")
                else:
                    print("⚠️ No action plan generated")

            else:
                print(f"❌ FAILED: {result.error_message}")
                print(f"💭 Rationale: {result.rationale}")

        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")

def test_unsupported_department():
    """Test handling of unsupported department categories"""
    print(f"\n" + "=" * 50)
    print("🚫 TESTING UNSUPPORTED DEPARTMENTS")
    print("=" * 50)

    # Test with unsupported department using OTHER fallback
    unsupported_decision = RouterDecision(
        department=DepartmentCategory.OTHER,  # Graceful fallback for unsupported
        confidence=0.85,
        urgency_indicators=["power outage"],
        reason="Electricity department request",
        keywords_detected=["power", "electricity"],
        degraded_mode_used=False,
        classification_source="llm"
    )

    result = process_department_request(
        original_request="Power is out in my area",
        router_decision=unsupported_decision,
        user_city="Lahore"
    )

    print(f"Request: Power outage")
    print(f"Department: {unsupported_decision}")
    # print(f"Success: {result.success}")
    # print(f"Error: {result.error_message}")

def test_agent_registry():
    """Test the agent registry functionality"""
    print(f"\n" + "=" * 50)
    print("🤖 TESTING AGENT REGISTRY")
    print("=" * 50)

    from apps.depts.agents.department_orchestrator_agent.agent import (
        get_specialized_agent,
        is_department_supported,
        DEPARTMENT_ORCHESTRATOR_AGENT
    )

    supported_categories = DEPARTMENT_ORCHESTRATOR_AGENT.get_supported_categories()
    print(f"Supported categories: {supported_categories}")

    for category in supported_categories:
        agent = get_specialized_agent(category)
        supported = is_department_supported(category)
        print(f"✅ {category}: Agent={agent is not None}, Supported={supported}")

    # Test unsupported category
    unsupported = "unsupported_dept"
    agent = get_specialized_agent(unsupported)
    supported = is_department_supported(unsupported)
    print(f"❌ {unsupported}: Agent={agent is not None}, Supported={supported}")

if __name__ == "__main__":
    # test_department_orchestrator()
    test_unsupported_department()
    test_agent_registry()