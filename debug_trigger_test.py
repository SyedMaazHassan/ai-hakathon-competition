#!/usr/bin/env python3
"""
Debug Trigger Test - Find the exact error
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

from apps.depts.services.trigger_orchestrator_service import (
    trigger_emergency_actions, EmailAction, ActionPriority, TriggerActionType
)
from apps.depts.agents.department_orchestrator_agent.pydantic_models import (
    DepartmentOrchestratorServiceOutput, ActionPlan, ActionStep, RequestPlan
)
from apps.depts.services.matcher_service import EntityInfo
from apps.depts.agents.router_agent.pydantic_models import RouterDecision
from apps.depts.choices import DepartmentCategory

# Import action services for individual testing
from apps.depts.services.actions.email_action_service import EmailActionService
from apps.depts.services.actions.sms_action_service import SMSActionService
from apps.depts.services.actions.voice_action_service import VoiceActionService

def simple_test():
    """Simple test to find the error"""

    print("🔍 Creating test data step by step...")

    # Step 1: Create EntityInfo
    print("1. Creating EntityInfo...")
    try:
        entity_info = EntityInfo(
            id="POL001",
            name="Test Police Station",
            phone="+92-300-1234567",
            city="Lahore",
            address="Test Address",
            distance_km=2.5,
            match_reason="Test match"
        )
        print("✅ EntityInfo created successfully")
    except Exception as e:
        print(f"❌ EntityInfo failed: {e}")
        return

    # Step 2: Create RouterDecision
    print("2. Creating RouterDecision...")
    try:
        router_decision = RouterDecision(
            department=DepartmentCategory.POLICE,
            confidence=0.9,
            urgency_indicators=["emergency"],
            reason="Test reason",
            keywords_detected=["test"],
            degraded_mode_used=False,
            classification_source="llm"
        )
        print("✅ RouterDecision created successfully")
    except Exception as e:
        print(f"❌ RouterDecision failed: {e}")
        return

    # Step 3: Create ActionPlan
    print("3. Creating ActionPlan...")
    try:
        action_plan = ActionPlan(
            immediate_actions=[
                ActionStep(
                    step_number=1,
                    action="Test immediate action",
                    timeline="0-5 minutes",
                    responsible_party="Police"
                )
            ],
            follow_up_actions=[
                ActionStep(
                    step_number=1,
                    action="Test follow-up",
                    timeline="1 hour",
                    responsible_party="Police"
                )
            ],
            estimated_resolution_time="30 minutes"
        )
        print("✅ ActionPlan created successfully")
    except Exception as e:
        print(f"❌ ActionPlan failed: {e}")
        return

    # Step 4: Create RequestPlan
    print("4. Creating RequestPlan...")
    try:
        request_plan = RequestPlan(
            incident_summary="Test incident",
            location_details="Test location",
            additional_context="Test context",
            required_response="Test response"
        )
        print("✅ RequestPlan created successfully")
    except Exception as e:
        print(f"❌ RequestPlan failed: {e}")
        return

    # Step 5: Create DepartmentOrchestratorServiceOutput
    print("5. Creating DepartmentOrchestratorServiceOutput...")
    try:
        dept_output = DepartmentOrchestratorServiceOutput(
            criticality="critical",
            action_plan=action_plan,
            request_plan=request_plan,
            rationale="Test rationale",
            communication_method="CALL",
            success=True
        )
        print("✅ DepartmentOrchestratorServiceOutput created successfully")
    except Exception as e:
        print(f"❌ DepartmentOrchestratorServiceOutput failed: {e}")
        return

    # Step 6: Call trigger_emergency_actions
    print("6. Calling trigger_emergency_actions...")
    try:
        result = trigger_emergency_actions(
            department_output=dept_output,
            entity_info=entity_info,
            router_decision=router_decision,
            user_phone="+92-300-1234567",
            user_email="test@example.com",
            user_coordinates={"lat": 31.5204, "lng": 74.3587}
        )
        print("✅ trigger_emergency_actions called successfully!")
        print(f"Success: {result.success}")
        print(f"Actions: {len(result.triggered_actions)}")

    except Exception as e:
        print(f"❌ trigger_emergency_actions failed: {e}")
        import traceback
        traceback.print_exc()

def test_email_service():
    """Test Email Action Service step by step"""

    print("\n📧 TESTING EMAIL SERVICE")
    print("=" * 50)

    # Step 1: Create EmailAction object
    print("1. Creating EmailAction object...")
    try:
        email_action = EmailAction(
            priority=ActionPriority.IMMEDIATE,
            title="Test Emergency Email",
            description="Testing email service",
            estimated_duration="30 seconds",
            recipient_email="hafizmaazhassan33@gmail.com",
            subject="Emergency Test Email",
            body="This is a test emergency email from the system."
        )
        print("✅ EmailAction created successfully")
        print(f"   Action Type: {email_action.action_type.value}")
        print(f"   Priority: {email_action.priority.value}")
        print(f"   Recipient: {email_action.recipient_email}")

    except Exception as e:
        print(f"❌ EmailAction creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 2: Create EmailActionService
    print("\n2. Creating EmailActionService...")
    try:
        email_service = EmailActionService()
        print("✅ EmailActionService created successfully")

    except Exception as e:
        print(f"❌ EmailActionService creation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Execute email action
    print("\n3. Executing email action...")
    try:
        result = email_service.execute_email_action(email_action)
        print("✅ Email action executed!")

        if result.get("success"):
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Recipient: {result.get('recipient', 'unknown')}")
            print(f"   Subject: {result.get('subject', 'unknown')}")
            if result.get("message_id"):
                print(f"   Message ID: {result['message_id']}")
            if result.get("note"):
                print(f"   Note: {result['note']}")
        else:
            print(f"   ❌ Email failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Email execution failed: {e}")
        import traceback
        traceback.print_exc()

def test_email_with_different_priorities():
    """Test email with different priority levels"""

    print("\n📊 TESTING EMAIL WITH DIFFERENT PRIORITIES")
    print("=" * 50)

    email_service = EmailActionService()
    priorities = [
        (ActionPriority.IMMEDIATE, "CRITICAL"),
        (ActionPriority.URGENT, "HIGH"),
        (ActionPriority.NORMAL, "MEDIUM"),
        (ActionPriority.SCHEDULED, "LOW")
    ]

    for priority, label in priorities:
        print(f"\n🎯 Testing {label} Priority Email...")

        try:
            email_action = EmailAction(
                priority=priority,
                title=f"{label} Priority Test Email",
                description=f"Testing {label.lower()} priority email",
                estimated_duration="30 seconds",
                recipient_email="test@example.com",
                subject=f"{label} Priority: Emergency Test",
                body=f"This is a {label.lower()} priority test email from the emergency system."
            )

            result = email_service.execute_email_action(email_action)

            if result.get("success"):
                print(f"   ✅ {label} email sent successfully")
                print(f"      Subject: {result.get('subject', 'N/A')}")
            else:
                print(f"   ❌ {label} email failed: {result.get('error')}")

        except Exception as e:
            print(f"   💥 {label} email exception: {e}")

def interactive_debug_menu():
    """Interactive menu for step-by-step testing"""

    print("\n" + "="*60)
    print("🔍 DEBUG TESTING MENU")
    print("="*60)
    print("1. Test Basic Trigger Orchestrator")
    print("2. Test Email Service Only")
    print("3. Test Email with Different Priorities")
    print("4. Test Email + SMS Combined")
    print("5. Run All Tests")
    print("0. Exit")
    print("-" * 40)

    while True:
        try:
            choice = input("\nSelect test to run (0-5): ").strip()

            if choice == "1":
                simple_test()
            elif choice == "2":
                test_email_service()
            elif choice == "3":
                test_email_with_different_priorities()
            elif choice == "4":
                test_email_service()
                print("\n" + "="*50)
                # Will add SMS test next
                print("SMS test coming next...")
            elif choice == "5":
                simple_test()
                test_email_service()
                test_email_with_different_priorities()
            elif choice == "0":
                print("\n👋 Debug testing complete!")
                break
            else:
                print("❌ Invalid choice. Please select 0-5.")

            input("\nPress Enter to return to menu...")

        except KeyboardInterrupt:
            print("\n\n👋 Testing interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Menu error: {e}")

if __name__ == "__main__":
    print("🔍 Starting Step-by-Step Debug Testing...")
    print("This will test each component individually to find issues.")

    interactive_debug_menu()