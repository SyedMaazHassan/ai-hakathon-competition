#!/usr/bin/env python3
"""
Test SMS Action Service - Independent Testing
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

from apps.depts.services.actions.sms_action_service import SMSActionService
from apps.depts.services.trigger_orchestrator_service import SMSAction, ActionPriority

def test_sms_service_basic():
    """Test basic SMS functionality"""
    print("🔹 TESTING SMS ACTION SERVICE")
    print("=" * 50)

    # Create SMS service
    sms_service = SMSActionService()
    print(f"📱 SMS Service initialized (Mock: {sms_service.use_mock})")

    # Create test SMS action
    test_sms = SMSAction(
        priority=ActionPriority.URGENT,
        title="Emergency SMS Test",
        description="Test SMS for emergency pipeline",
        estimated_duration="30 seconds",
        recipient_phone="+92-300-1234567",
        message="🚨 EMERGENCY TEST: This is a test message from the Emergency Pipeline System. Your request has been processed and help is being dispatched. Reference: TEST-001"
    )

    print(f"\n📤 Sending test SMS to: {test_sms.recipient_phone}")
    print(f"📄 Message preview: {test_sms.message[:60]}...")

    # Execute SMS action
    result = sms_service.execute_sms_action(test_sms)

    print(f"\n📊 SMS EXECUTION RESULT:")
    print(f"✅ Success: {result['success']}")
    print(f"📱 Service Type: {result.get('service_type', 'unknown')}")
    print(f"📞 Recipient: {result.get('recipient', 'unknown')}")
    print(f"🆔 Message ID: {result.get('message_id', 'unknown')}")
    print(f"📝 Preview: {result.get('message_preview', 'unknown')}")

    if not result['success']:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

    return result

def test_different_priorities():
    """Test SMS with different priority levels"""
    print("\n🔹 TESTING DIFFERENT PRIORITY LEVELS")
    print("=" * 50)

    sms_service = SMSActionService()
    priorities = [
        (ActionPriority.IMMEDIATE, "Cardiac arrest reported"),
        (ActionPriority.URGENT, "House fire emergency"),
        (ActionPriority.NORMAL, "Traffic accident"),
        (ActionPriority.SCHEDULED, "Noise complaint")
    ]

    results = []
    for priority, message in priorities:
        print(f"\n🚨 Testing {priority.value.upper()} priority")

        test_sms = SMSAction(
            priority=priority,
            title=f"{priority.value.title()} Alert",
            description=f"Test {priority.value} priority message",
            estimated_duration="30 seconds",
            recipient_phone="+92-301-2697601",
            message=message
        )

        result = sms_service.execute_sms_action(test_sms)
        results.append((priority.value, result['success']))

        print(f"   {'✅' if result['success'] else '❌'} {priority.value}: {result['success']}")
        if result['success']:
            print(f"   📝 Preview: {result.get('message_preview', 'N/A')}")

    print(f"\n📊 PRIORITY TESTS SUMMARY:")
    for priority, success in results:
        print(f"   {priority}: {'✅ PASS' if success else '❌ FAIL'}")

    return results

def test_bulk_sms():
    """Test bulk SMS functionality"""
    print("\n🔹 TESTING BULK SMS")
    print("=" * 50)

    sms_service = SMSActionService()

    # Create multiple SMS actions
    sms_actions = [
        SMSAction(
            priority=ActionPriority.URGENT,
            title="Emergency Notification",
            description="Emergency alert to multiple recipients",
            estimated_duration="30 seconds",
            recipient_phone="+92-300-1111111",
            message="Emergency alert: Evacuation notice for Block A"
        ),
        SMSAction(
            priority=ActionPriority.URGENT,
            title="Emergency Notification",
            description="Emergency alert to multiple recipients",
            estimated_duration="30 seconds",
            recipient_phone="+92-300-2222222",
            message="Emergency alert: Evacuation notice for Block B"
        ),
        SMSAction(
            priority=ActionPriority.IMMEDIATE,
            title="Critical Alert",
            description="Critical emergency notification",
            estimated_duration="15 seconds",
            recipient_phone="+92-300-3333333",
            message="CRITICAL: Immediate evacuation required"
        )
    ]

    print(f"📤 Sending bulk SMS to {len(sms_actions)} recipients...")

    result = sms_service.send_bulk_sms(sms_actions)

    print(f"\n📊 BULK SMS RESULT:")
    print(f"✅ Success: {result['success']}")
    print(f"📤 Total Sent: {result.get('total_sent', 0)}")
    print(f"❌ Total Failed: {result.get('total_failed', 0)}")

    if 'results' in result:
        print(f"\n📋 INDIVIDUAL RESULTS:")
        for i, res in enumerate(result['results'], 1):
            status = "✅" if res['success'] else "❌"
            print(f"   {i}. {status} {res['phone']} - {res.get('message_id', res.get('error', 'Unknown'))}")

    return result

def test_error_handling():
    """Test error handling scenarios"""
    print("\n🔹 TESTING ERROR HANDLING")
    print("=" * 50)

    sms_service = SMSActionService()

    # Test with invalid phone number
    print("🧪 Testing invalid phone number...")
    invalid_sms = SMSAction(
        priority=ActionPriority.NORMAL,
        title="Invalid Test",
        description="Testing invalid phone number",
        estimated_duration="30 seconds",
        recipient_phone="invalid-phone",
        message="This should fail"
    )

    result = sms_service.execute_sms_action(invalid_sms)
    print(f"   Expected failure: {'✅' if not result['success'] else '❌'}")
    if not result['success']:
        print(f"   Error: {result.get('error', 'Unknown')}")

    # Test with very long message
    print("\n🧪 Testing very long message...")
    long_message = "This is a very long message " * 100  # ~2700 characters
    long_sms = SMSAction(
        priority=ActionPriority.SCHEDULED,
        title="Long Message Test",
        description="Testing message length limits",
        estimated_duration="60 seconds",
        recipient_phone="+92-300-9999999",
        message=long_message
    )

    result = sms_service.execute_sms_action(long_sms)
    print(f"   Long message handling: {'✅' if result['success'] else '❌'}")
    if not result['success']:
        print(f"   Error: {result.get('error', 'Unknown')}")

def main():
    """Run all SMS tests"""
    print("🚀 STARTING SMS ACTION SERVICE TESTS")
    print("=" * 70)

    try:
        # Basic functionality test
        basic_result = test_sms_service_basic()

        # Priority levels test
        priority_results = test_different_priorities()

        # Bulk SMS test
        bulk_result = test_bulk_sms()

        # Error handling test
        test_error_handling()

        print("\n🎉 ALL SMS TESTS COMPLETED!")
        print("=" * 70)

        # Summary
        total_tests = 1 + len(priority_results) + 1
        successful_tests = (
            (1 if basic_result['success'] else 0) +
            sum(1 for _, success in priority_results if success) +
            (1 if bulk_result['success'] else 0)
        )

        print(f"📊 TEST SUMMARY: {successful_tests}/{total_tests} tests passed")

        if successful_tests == total_tests:
            print("✅ SMS Action Service is working perfectly!")
        else:
            print("⚠️ Some tests failed - check logs above")

    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()