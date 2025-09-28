#!/usr/bin/env python3
"""
Debug Email Actions - Check what's happening with emails
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.services.simplified_emergency_pipeline import SimplifiedEmergencyPipeline, EmergencyRequest
from apps.depts.services.actions.email_action_service import EmailActionService

def debug_email_actions():
    """Debug why emails aren't being sent"""
    print("🔍 DEBUGGING EMAIL ACTIONS")
    print("=" * 50)

    # Test email configuration
    print("1. Testing email configuration...")
    email_service = EmailActionService()
    config_test = email_service.test_email_config()
    print(f"   Email backend: {config_test.get('backend', 'Unknown')}")
    print(f"   Email host: {config_test.get('host', 'Unknown')}")
    print(f"   From email: {config_test.get('from_email', 'Unknown')}")
    print(f"   Config success: {config_test.get('success', False)}")

    # Test pipeline with email user
    print("\n2. Testing pipeline with user email...")
    pipeline = SimplifiedEmergencyPipeline()

    test_request = EmergencyRequest(
        request_text="Fire brigade is needed, house is on fire!",
        user_phone="+923012697601",
        user_email="hafizmaazhassan33@gmail.com",  # User should receive email
        user_city="Karachi",
        user_coordinates={"lat": 31.5497, "lng": 74.3436},
        user_name="Test User"
    )

    result = pipeline.process_emergency_request(test_request)

    print(f"   Pipeline success: {result.success}")
    # print(f"   Actions triggered: {result.actions_triggered}")
    print(f"   Actions executed: {result.actions_executed}")

    if hasattr(result, 'action_details') and result.action_details:
        print(f"\n3. Action execution details:")
        for i, action in enumerate(result.action_details, 1):
            if action.get('action_type') == 'email':
                print(f"   {i}. EMAIL to {action.get('recipient', 'unknown')}")
                print(f"      Success: {action.get('success', False)}")
                print(f"      Subject: {action.get('subject', 'No subject')[:50]}...")
                if not action.get('success'):
                    print(f"      Error: {action.get('error', 'Unknown error')}")
            elif action.get('action_type') == 'sms':
                print(f"   {i}. SMS to {action.get('recipient', 'unknown')}")
                print(f"      Success: {action.get('success', False)}")
                if not action.get('success'):
                    print(f"      Error: {action.get('error', 'Unknown error')}")

    print(f"\n4. User should receive:")
    print(f"   - SMS with Google Maps link (if phone provided)")
    print(f"   - Email with actionable steps (if email provided)")
    print(f"   - Department should receive detailed emergency email")

if __name__ == "__main__":
    debug_email_actions()