#!/usr/bin/env python3
"""
Test Voice Integration - EmergencyCallAgent through ActionExecutor
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

from apps.depts.services.trigger_orchestrator_service import VoiceCallAction, ActionPriority
from apps.depts.services.actions.action_executor import ActionExecutor

def test_voice_integration():
    """Test that VoiceCallAction properly routes to EmergencyCallAgent"""

    print("🎙️ Testing Voice Integration...")
    print("=" * 50)

    # Create test voice action
    voice_action = VoiceCallAction(
        priority=ActionPriority.IMMEDIATE,
        title="Fire Emergency Call",
        description="Emergency call to fire department",
        estimated_duration="3 minutes",
        recipient_phone="+923472533106",  # Your test number
        call_script="CRITICAL EMERGENCY: House fire with trapped residents. "
                   "Location: Model Town, Lahore. Immediate response required.",
        max_duration_minutes=5
    )

    print(f"📞 Test Voice Action:")
    print(f"   Recipient: {voice_action.recipient_phone}")
    print(f"   Priority: {voice_action.priority.value}")
    print(f"   Script: {voice_action.call_script[:80]}...")

    # Initialize ActionExecutor
    executor = ActionExecutor()

    # Execute the voice action
    print(f"\n🚀 Executing voice action through ActionExecutor...")
    result = executor.execute_single_action(voice_action)

    print(f"\n📊 EXECUTION RESULT:")
    print(f"✅ Success: {result.get('success', False)}")
    print(f"🎯 Action Type: {result.get('action_type', 'unknown')}")
    print(f"📞 Recipient: {result.get('recipient', 'unknown')}")
    print(f"🆔 Call ID: {result.get('call_id', 'unknown')}")
    print(f"⏱️ Duration: {result.get('estimated_duration', 'unknown')}")
    print(f"🔧 Service: {result.get('service', 'unknown')}")

    if not result.get('success'):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    if result.get('script_preview'):
        print(f"📝 Script Preview: {result['script_preview']}")

    return result.get('success', False)

if __name__ == "__main__":
    try:
        success = test_voice_integration()

        print(f"\n{'='*50}")
        if success:
            print("✅ Voice integration test PASSED!")
            print("🎉 EmergencyCallAgent is properly integrated through ActionExecutor")
        else:
            print("❌ Voice integration test FAILED!")
            print("💥 Check the error messages above")

    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()