#!/usr/bin/env python3
"""
Test Action Services - Manual Testing with Sample Inputs
Test each action service individually with realistic emergency scenarios
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

from apps.depts.services.actions.email_action_service import EmailActionService
from apps.depts.services.actions.sms_action_service import SMSActionService
from apps.depts.services.actions.voice_action_service import VoiceActionService
from apps.depts.services.actions.calendar_action_service import CalendarActionService
from apps.depts.services.actions.maps_action_service import MapsActionService
from apps.depts.services.actions.action_executor import ActionExecutor

from apps.depts.services.trigger_orchestrator_service import (
    EmailAction, SMSAction, VoiceCallAction, CalendarBookingAction,
    NearbySearchAction, MapsDirectionsAction, EmergencyBroadcastAction,
    FollowupScheduleAction, ActionPriority, TriggerActionType
)

def print_separator(title):
    """Print section separator"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {title}")
    print(f"{'='*60}")

def print_result(result):
    """Print action result in formatted way"""
    if result.get("success"):
        print("✅ SUCCESS!")
        print(f"Status: {result.get('status', 'completed')}")
        if result.get("action_type"):
            print(f"Action Type: {result['action_type']}")
        if result.get("recipient"):
            print(f"Recipient: {result['recipient']}")
        if result.get("estimated_delivery"):
            print(f"Delivery Time: {result['estimated_delivery']}")
        if result.get("message_id"):
            print(f"Message ID: {result['message_id']}")
        if result.get("note"):
            print(f"Note: {result['note']}")
    else:
        print("❌ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")

def test_email_actions():
    """Test Email Action Service"""
    print_separator("EMAIL ACTION SERVICE")

    email_service = EmailActionService()

    # Test 1: Critical Emergency Email
    print("\n1️⃣ Critical Emergency Email")
    print("-" * 40)

    critical_email = EmailAction(
        priority=ActionPriority.IMMEDIATE,
        title="Critical Police Emergency",
        description="Immediate police response required",
        estimated_duration="30 seconds",
        recipient_email="emergency@testdomain.com",
        subject="Armed Robbery in Progress",
        body="CRITICAL EMERGENCY: Armed robbery reported at Main Street Market.\n\n"
             "Location: 123 Main Street, Lahore\n"
             "Time: Immediate response required\n"
             "Contact: +92-300-1234567\n\n"
             "Multiple suspects armed with weapons. Citizens evacuated.\n"
             "Police response team dispatched immediately.",
        department_cc="police@lahore.gov.pk"
    )

    result = email_service.execute_email_action(critical_email)
    print_result(result)

    # Test 2: Standard Service Email
    print("\n2️⃣ Standard Service Email")
    print("-" * 40)

    standard_email = EmailAction(
        priority=ActionPriority.NORMAL,
        title="Service Request Confirmation",
        description="Standard email confirmation",
        estimated_duration="1 minute",
        recipient_email="citizen@example.com",
        subject="Your Cybercrime Complaint Has Been Received",
        body="Dear Citizen,\n\n"
             "Your cybercrime complaint has been successfully logged in our system.\n\n"
             "Complaint Details:\n"
             "- Type: Online Banking Fraud\n"
             "- Reference: CYB-2024-001234\n"
             "- Department: FIA Cybercrime\n\n"
             "Expected Response: Within 48-72 hours\n\n"
             "Thank you for using our emergency services platform."
    )

    result = email_service.execute_email_action(standard_email)
    print_result(result)

def test_sms_actions():
    """Test SMS Action Service"""
    print_separator("SMS ACTION SERVICE")

    sms_service = SMSActionService()

    # Test 1: Critical Emergency SMS
    print("\n1️⃣ Critical Emergency SMS")
    print("-" * 40)

    critical_sms = SMSAction(
        priority=ActionPriority.IMMEDIATE,
        title="Emergency Alert SMS",
        description="Immediate emergency notification",
        estimated_duration="10 seconds",
        recipient_phone="+92-300-1234567",
        message="Fire emergency at your building reported. Rescue 1122 dispatched. Evacuate immediately via stairwell. Do not use elevator. Help arriving in 5-8 minutes.",
        sender_name="Rescue 1122"
    )

    result = sms_service.execute_sms_action(critical_sms)
    print_result(result)

    # Test 2: High Priority SMS
    print("\n2️⃣ High Priority SMS")
    print("-" * 40)

    urgent_sms = SMSAction(
        priority=ActionPriority.URGENT,
        title="Medical Emergency SMS",
        description="Urgent medical response",
        estimated_duration="15 seconds",
        recipient_phone="+92-301-9876543",
        message="Medical emergency logged. Ambulance from Mayo Hospital dispatched to your location. ETA: 12-15 minutes. Stay with patient. Keep airway clear.",
        sender_name="Emergency Medical Services"
    )

    result = sms_service.execute_sms_action(urgent_sms)
    print_result(result)

def test_voice_actions():
    """Test Voice Action Service"""
    print_separator("VOICE ACTION SERVICE")

    voice_service = VoiceActionService()

    # Test 1: Critical Emergency Voice Call
    print("\n1️⃣ Critical Emergency Voice Call")
    print("-" * 40)

    critical_voice = VoiceCallAction(
        priority=ActionPriority.IMMEDIATE,
        title="Emergency Police Voice Alert",
        description="Immediate police notification call",
        estimated_duration="2 minutes",
        recipient_phone="+92-42-35714000",
        call_script="CRITICAL EMERGENCY ALERT: Armed robbery in progress at Main Street Market, Gulberg, Lahore. "
                   "Multiple suspects with weapons reported. Citizens evacuated. Immediate police response required. "
                   "Location coordinates: 31.5204, 74.3587. Contact number: +92-300-1234567.",
        max_duration_minutes=3
    )

    result = voice_service.execute_voice_action(critical_voice)
    print_result(result)

    # Test 2: Department Notification Call
    print("\n2️⃣ Department Notification Call")
    print("-" * 40)

    dept_voice = VoiceCallAction(
        priority=ActionPriority.URGENT,
        title="Department Alert Call",
        description="Urgent department notification",
        estimated_duration="3 minutes",
        recipient_phone="1122",
        call_script="URGENT: Fire emergency reported at residential building. Location: Block B, Model Town, Lahore. "
                   "Multiple floors affected. Residents trapped on upper floors. Fire brigade response needed immediately. "
                   "Contact person on site: +92-301-5555555.",
        max_duration_minutes=5
    )

    result = voice_service.execute_voice_action(dept_voice)
    print_result(result)

def test_calendar_actions():
    """Test Calendar Action Service"""
    print_separator("CALENDAR ACTION SERVICE")

    calendar_service = CalendarActionService()

    # Test 1: Emergency Consultation Booking
    print("\n1️⃣ Emergency Consultation Booking")
    print("-" * 40)

    consultation_booking = CalendarBookingAction(
        priority=ActionPriority.NORMAL,
        title="Cybercrime Consultation",
        description="Schedule follow-up for cybercrime case",
        estimated_duration="2 minutes",
        appointment_title="Cybercrime Case Follow-up: Online Banking Fraud",
        appointment_description="Follow-up consultation for cybercrime complaint CYB-2024-001234. "
                              "Discuss investigation progress and additional evidence collection.",
        duration_minutes=45,
        preferred_time_slots=["Next business day 10-11 AM", "Next business day 3-4 PM"],
        attendee_emails=["citizen@example.com", "investigator@fia.gov.pk"]
    )

    result = calendar_service.execute_calendar_action(consultation_booking)
    print_result(result)

    # Test 2: Medical Follow-up Appointment
    print("\n2️⃣ Medical Follow-up Appointment")
    print("-" * 40)

    medical_booking = CalendarBookingAction(
        priority=ActionPriority.SCHEDULED,
        title="Medical Follow-up",
        description="Post-emergency medical check",
        estimated_duration="1 minute",
        appointment_title="Post-Emergency Medical Check",
        appointment_description="Follow-up appointment after emergency medical response. "
                              "Assessment of recovery and any ongoing medical needs.",
        duration_minutes=30,
        preferred_time_slots=["Next business day 9-11 AM"],
        attendee_emails=["patient@example.com"]
    )

    result = calendar_service.execute_calendar_action(medical_booking)
    print_result(result)

def test_maps_actions():
    """Test Maps Action Service"""
    print_separator("MAPS ACTION SERVICE")

    maps_service = MapsActionService()

    # Test 1: Nearby Hospitals Search
    print("\n1️⃣ Nearby Hospitals Search")
    print("-" * 40)

    hospital_search = NearbySearchAction(
        priority=ActionPriority.URGENT,
        title="Emergency Hospital Search",
        description="Find nearby hospitals for backup",
        estimated_duration="1 minute",
        search_query="hospital emergency",
        location_lat=31.5204,  # Gulberg, Lahore
        location_lng=74.3587,
        radius_km=10,
        result_limit=5
    )

    result = maps_service.execute_nearby_search(hospital_search)
    print_result(result)
    if result.get("success") and result.get("results"):
        print(f"\n🏥 Found {result['results_found']} hospitals:")
        for i, hospital in enumerate(result['results'][:3], 1):
            print(f"  {i}. {hospital['name']}")
            print(f"     Distance: {hospital.get('distance_km', 'N/A')} km")
            print(f"     Rating: {hospital.get('rating', 'N/A')}/5")

    # Test 2: Police Station Directions
    print("\n2️⃣ Police Station Directions")
    print("-" * 40)

    directions_action = MapsDirectionsAction(
        priority=ActionPriority.URGENT,
        title="Route to Police Station",
        description="Directions for police response",
        estimated_duration="30 seconds",
        origin_address="31.5204,74.3587",  # Emergency location
        destination_address="Gulberg Police Station, Lahore",
        travel_mode="driving",
        optimize_route=True
    )

    result = maps_service.execute_directions_action(directions_action)
    print_result(result)
    if result.get("success"):
        print(f"\n🗺️ Route Details:")
        print(f"  Distance: {result.get('total_distance_km', 'N/A')} km")
        print(f"  Duration: {result.get('total_duration_minutes', 'N/A')} minutes")
        print(f"  Mode: {result.get('travel_mode', 'driving')}")

def test_action_executor():
    """Test Action Executor with Multiple Actions"""
    print_separator("ACTION EXECUTOR - MULTI-ACTION TEST")

    executor = ActionExecutor()

    # Create a mix of actions for testing
    test_actions = [
        EmailAction(
            priority=ActionPriority.IMMEDIATE,
            title="Emergency Email",
            description="Critical email",
            estimated_duration="30 seconds",
            recipient_email="test@example.com",
            subject="Emergency Test",
            body="This is a test emergency email."
        ),
        SMSAction(
            priority=ActionPriority.URGENT,
            title="Emergency SMS",
            description="Critical SMS",
            estimated_duration="10 seconds",
            recipient_phone="+92-300-1234567",
            message="Emergency test SMS message."
        ),
        VoiceCallAction(
            priority=ActionPriority.IMMEDIATE,
            title="Emergency Call",
            description="Critical call",
            estimated_duration="2 minutes",
            recipient_phone="+92-300-9999999",
            call_script="This is a test emergency call."
        )
    ]

    print(f"\n📋 Executing {len(test_actions)} actions in parallel...")
    print("-" * 40)

    result = executor.execute_multiple_actions(test_actions, parallel=True)

    print(f"✅ Execution Summary:")
    print(f"  Total Actions: {result['total_actions']}")
    print(f"  Successful: {result['successful_actions']}")
    print(f"  Failed: {result['failed_actions']}")
    print(f"  Mode: {result['execution_mode']}")

    print(f"\n📊 Individual Results:")
    for i, action_result in enumerate(result['results'], 1):
        status = "✅" if action_result.get("success") else "❌"
        action_type = action_result.get("action_type", "unknown")
        print(f"  {i}. {status} {action_type}")

def interactive_menu():
    """Interactive menu for testing individual services"""

    print("\n" + "="*60)
    print("🧪 ACTION SERVICES TESTING MENU")
    print("="*60)
    print("1. Test Email Actions")
    print("2. Test SMS Actions")
    print("3. Test Voice Call Actions")
    print("4. Test Calendar Actions")
    print("5. Test Maps Actions")
    print("6. Test Action Executor (Multi-Action)")
    print("7. Run All Tests")
    print("0. Exit")
    print("-" * 40)

    while True:
        try:
            choice = input("\nSelect test to run (0-7): ").strip()

            if choice == "1":
                test_email_actions()
            elif choice == "2":
                test_sms_actions()
            elif choice == "3":
                test_voice_actions()
            elif choice == "4":
                test_calendar_actions()
            elif choice == "5":
                test_maps_actions()
            elif choice == "6":
                test_action_executor()
            elif choice == "7":
                test_email_actions()
                test_sms_actions()
                test_voice_actions()
                test_calendar_actions()
                test_maps_actions()
                test_action_executor()
            elif choice == "0":
                print("\n👋 Testing complete. Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 0-7.")

            input("\nPress Enter to return to menu...")

        except KeyboardInterrupt:
            print("\n\n👋 Testing interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Action Services Testing...")
    print("This will test each action service with realistic emergency scenarios.")
    print("All services work in MOCK mode for demo purposes.")

    interactive_menu()