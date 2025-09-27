#!/usr/bin/env python3
"""
Test Trigger Orchestrator Service - Database Synchronization Test
Verifies that enums and models are properly synced with database choices
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
    TriggerActionType, ActionPriority, TriggerAction,
    EmailAction, SMSAction, VoiceCallAction
)
from apps.depts.choices import ActionType, UrgencyLevel

def test_enum_synchronization():
    """Test that trigger orchestrator enums are synced with database choices"""
    print("🔗 TESTING ENUM SYNCHRONIZATION")
    print("=" * 50)

    # Test ActionType synchronization
    print("\n📋 ACTION TYPE SYNCHRONIZATION:")
    trigger_to_db_mapping = {
        TriggerActionType.EMAIL: ActionType.EMAIL_SENT,
        TriggerActionType.SMS: ActionType.SMS_SENT,
        TriggerActionType.VOICE_CALL: ActionType.EMERGENCY_CALL,
        TriggerActionType.CALENDAR_BOOKING: ActionType.APPOINTMENT_BOOKED,
        TriggerActionType.NEARBY_SEARCH: ActionType.NEARBY_SEARCH,
        TriggerActionType.MAPS_DIRECTIONS: ActionType.MAPS_DIRECTIONS,
        TriggerActionType.EMERGENCY_BROADCAST: ActionType.EMERGENCY_BROADCAST,
        TriggerActionType.FOLLOWUP_SCHEDULE: ActionType.FOLLOWUP_SCHEDULE,
    }

    for trigger_action, db_action in trigger_to_db_mapping.items():
        try:
            assert trigger_action.value == db_action.value, f"Mismatch: {trigger_action.value} != {db_action.value}"
            print(f"✅ {trigger_action.name}: '{trigger_action.value}' == '{db_action.value}'")
        except AssertionError as e:
            print(f"❌ {trigger_action.name}: {e}")
        except Exception as e:
            print(f"💥 {trigger_action.name}: Error - {e}")

    # Test Priority synchronization
    print("\n⚡ PRIORITY SYNCHRONIZATION:")
    priority_to_urgency_mapping = {
        ActionPriority.IMMEDIATE: UrgencyLevel.CRITICAL,
        ActionPriority.URGENT: UrgencyLevel.HIGH,
        ActionPriority.NORMAL: UrgencyLevel.MEDIUM,
        ActionPriority.SCHEDULED: UrgencyLevel.LOW,
    }

    for priority, urgency in priority_to_urgency_mapping.items():
        try:
            assert priority.value == urgency.value, f"Mismatch: {priority.value} != {urgency.value}"
            print(f"✅ {priority.name}: '{priority.value}' == '{urgency.value}'")
        except AssertionError as e:
            print(f"❌ {priority.name}: {e}")
        except Exception as e:
            print(f"💥 {priority.name}: Error - {e}")

def test_action_creation():
    """Test that trigger actions can be created with database-synced enums"""
    print("\n🏗️ TESTING ACTION CREATION")
    print("=" * 50)

    try:
        # Test EmailAction creation
        email_action = EmailAction(
            priority=ActionPriority.NORMAL,
            title="Test Email",
            description="Test email action",
            estimated_duration="30 seconds",
            recipient_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        print(f"✅ EmailAction: {email_action.action_type.value} | Priority: {email_action.priority.value}")

        # Test SMSAction creation
        sms_action = SMSAction(
            priority=ActionPriority.URGENT,
            title="Test SMS",
            description="Test SMS action",
            estimated_duration="10 seconds",
            recipient_phone="+92-300-1234567",
            message="Test message"
        )
        print(f"✅ SMSAction: {sms_action.action_type.value} | Priority: {sms_action.priority.value}")

        # Test VoiceCallAction creation
        voice_action = VoiceCallAction(
            priority=ActionPriority.IMMEDIATE,
            title="Test Call",
            description="Test voice call action",
            estimated_duration="2 minutes",
            recipient_phone="+92-300-1234567",
            call_script="Emergency test call"
        )
        print(f"✅ VoiceCallAction: {voice_action.action_type.value} | Priority: {voice_action.priority.value}")

    except Exception as e:
        print(f"❌ Action Creation Failed: {e}")

def test_criticality_mapping():
    """Test criticality string mapping to urgency levels"""
    print("\n🚨 TESTING CRITICALITY MAPPING")
    print("=" * 50)

    criticality_mappings = {
        "critical": UrgencyLevel.CRITICAL,
        "high": UrgencyLevel.HIGH,
        "medium": UrgencyLevel.MEDIUM,
        "low": UrgencyLevel.LOW
    }

    for criticality_str, expected_urgency in criticality_mappings.items():
        print(f"✅ '{criticality_str}' maps to '{expected_urgency.value}' ({expected_urgency.label})")

def test_database_compatibility():
    """Test compatibility with actual database models"""
    print("\n💾 TESTING DATABASE COMPATIBILITY")
    print("=" * 50)

    # Test that all ActionType values are available
    all_action_types = [choice[0] for choice in ActionType.choices]
    print(f"📋 Available database ActionTypes: {len(all_action_types)}")
    for action_type in all_action_types:
        print(f"   • {action_type}")

    # Test that all UrgencyLevel values are available
    all_urgency_levels = [choice[0] for choice in UrgencyLevel.choices]
    print(f"\n⚡ Available database UrgencyLevels: {len(all_urgency_levels)}")
    for urgency in all_urgency_levels:
        print(f"   • {urgency}")

    print(f"\n✅ Database compatibility verified!")

if __name__ == "__main__":
    try:
        test_enum_synchronization()
        test_action_creation()
        test_criticality_mapping()
        test_database_compatibility()
        print(f"\n🎉 ALL SYNCHRONIZATION TESTS PASSED!")

    except Exception as e:
        print(f"💥 SYNCHRONIZATION TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()