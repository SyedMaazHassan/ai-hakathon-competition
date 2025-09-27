#!/usr/bin/env python3
"""
Test Emergency Pipeline Service - Complete End-to-End Flow
Tests the complete emergency response pipeline from citizen request to action execution
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

from apps.depts.services.emergency_pipeline_service import (
    EmergencyPipelineService, CitizenRequest, process_citizen_emergency
)

def print_separator(title):
    """Print section separator"""
    print(f"\n{'='*70}")
    print(f"🚨 {title}")
    print(f"{'='*70}")

def print_pipeline_result(result):
    """Print formatted pipeline result"""

    print(f"\n📊 PIPELINE EXECUTION SUMMARY")
    print(f"{'='*50}")
    print(f"🆔 Request ID: {result.request_id}")
    print(f"⏱️ Total Duration: {result.total_duration_ms}ms")
    print(f"✅ Success: {result.pipeline_success}")

    if result.pipeline_success:
        print(f"🏛️ Department: {result.department_assigned}")
        print(f"🎯 Entity: {result.entity_matched}")
        print(f"🚨 Criticality: {result.criticality_level}")
        print(f"⚡ Actions Triggered: {result.actions_triggered}")
        print(f"🚀 Actions Executed: {result.actions_executed}")
        print(f"📞 Reference: {result.reference_number}")
    else:
        print(f"❌ Error: {result.error_message}")
        print(f"🔧 Degraded Mode: {result.degraded_mode}")

    print(f"\n📋 PIPELINE STEPS ({len(result.steps_executed)} steps)")
    print(f"{'='*50}")

    for i, step in enumerate(result.steps_executed, 1):
        status = "✅" if step.success else "❌"
        print(f"{i}. {status} {step.step_name} ({step.duration_ms}ms)")

        if step.success and step.output:
            for key, value in list(step.output.items())[:3]:  # Show first 3 items
                print(f"   • {key}: {value}")
        elif not step.success and step.error_message:
            print(f"   💥 Error: {step.error_message}")

    print(f"\n💬 CITIZEN MESSAGE:")
    print(f"{'='*50}")
    print(f"{result.citizen_message}")

def test_critical_police_emergency():
    """Test critical police emergency scenario"""

    print_separator("CRITICAL POLICE EMERGENCY")

    print("📞 Scenario: Armed robbery in progress")
    print("Location: Gulberg, Lahore")
    print("User has phone and coordinates")

    try:
        result = process_citizen_emergency(
            request_text="Armed men just robbed my jewelry shop at gunpoint! They threatened customers and took everything. Please send police immediately!",
            user_phone="+92-300-1234567",
            user_email="shopowner@example.com",
            user_city="Lahore",
            user_coordinates={"lat": 31.5204, "lng": 74.3587}
        )

        print_pipeline_result(result)

    except Exception as e:
        print(f"💥 Pipeline Test Failed: {e}")
        import traceback
        traceback.print_exc()

def test_medical_emergency():
    """Test medical emergency scenario"""

    print_separator("MEDICAL EMERGENCY")

    print("🏥 Scenario: Heart attack emergency")
    print("Location: Model Town, Lahore")
    print("User has phone only")

    try:
        result = process_citizen_emergency(
            request_text="My father is having chest pain and difficulty breathing. He's sweating and says his arm hurts. Need ambulance urgently!",
            user_phone="+92-301-9876543",
            user_city="Lahore"
        )

        print_pipeline_result(result)

    except Exception as e:
        print(f"💥 Pipeline Test Failed: {e}")

def test_fire_emergency():
    """Test fire emergency scenario"""

    print_separator("FIRE EMERGENCY")

    print("🔥 Scenario: Building fire with people trapped")
    print("Location: DHA, Lahore")
    print("User has full details")

    try:
        result = process_citizen_emergency(
            request_text="There's a big fire in our apartment building! Smoke everywhere and people are trapped on the 4th floor. Fire brigade needed now!",
            user_phone="+92-302-5555555",
            user_email="resident@example.com",
            user_city="Lahore",
            user_coordinates={"lat": 31.4697, "lng": 74.4142}
        )

        print_pipeline_result(result)

    except Exception as e:
        print(f"💥 Pipeline Test Failed: {e}")

def test_minimal_request():
    """Test minimal request with just text"""

    print_separator("MINIMAL REQUEST")

    print("📝 Scenario: Basic emergency request")
    print("Location: No location provided")
    print("Contact: No contact provided")

    try:
        result = process_citizen_emergency(
            request_text="Please help! Someone broke into my house!"
        )

        print_pipeline_result(result)

    except Exception as e:
        print(f"💥 Pipeline Test Failed: {e}")

def interactive_pipeline_menu():
    """Interactive menu for testing different scenarios"""

    print("\n" + "="*70)
    print("🚨 EMERGENCY PIPELINE TESTING MENU")
    print("="*70)
    print("1. Critical Police Emergency (Armed Robbery)")
    print("2. Medical Emergency (Heart Attack)")
    print("3. Fire Emergency (Building Fire)")
    print("4. Minimal Request (Basic Test)")
    print("5. Custom Emergency Request")
    print("6. Run All Scenarios")
    print("0. Exit")
    print("-" * 50)

    while True:
        try:
            choice = input("\nSelect test scenario (0-6): ").strip()

            if choice == "1":
                test_critical_police_emergency()
            elif choice == "2":
                test_medical_emergency()
            elif choice == "3":
                test_fire_emergency()
            elif choice == "4":
                test_minimal_request()
            elif choice == "5":
                test_custom_request()
            elif choice == "6":
                test_critical_police_emergency()
                test_medical_emergency()
                test_fire_emergency()
                test_minimal_request()
            elif choice == "0":
                print("\n👋 Pipeline testing complete!")
                break
            else:
                print("❌ Invalid choice. Please select 0-6.")

            input("\nPress Enter to return to menu...")

        except KeyboardInterrupt:
            print("\n\n👋 Testing interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Menu error: {e}")

def test_custom_request():
    """Test custom emergency request"""

    print_separator("CUSTOM EMERGENCY REQUEST")

    try:
        print("Enter your custom emergency details:")

        request_text = input("Emergency description: ").strip()
        if not request_text:
            print("❌ Emergency description is required")
            return

        user_phone = input("Phone number (optional): ").strip() or None
        user_email = input("Email (optional): ").strip() or None
        user_city = input("City (optional): ").strip() or None

        coordinates = None
        lat = input("Latitude (optional): ").strip()
        lng = input("Longitude (optional): ").strip()

        if lat and lng:
            try:
                coordinates = {"lat": float(lat), "lng": float(lng)}
            except ValueError:
                print("⚠️ Invalid coordinates, ignoring...")

        print(f"\n🚨 Processing custom emergency request...")

        result = process_citizen_emergency(
            request_text=request_text,
            user_phone=user_phone,
            user_email=user_email,
            user_city=user_city,
            user_coordinates=coordinates
        )

        print_pipeline_result(result)

    except Exception as e:
        print(f"💥 Custom request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Emergency Pipeline Testing...")
    print("This tests the complete end-to-end emergency response flow.")
    print("From citizen request → router → matcher → orchestrator → actions")

    interactive_pipeline_menu()