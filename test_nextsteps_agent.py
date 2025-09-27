#!/usr/bin/env python3
"""
Test Next-Steps Agent - Citizen Communication Testing
Tests the Next-Steps Agent with Urdu/English responses
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

from apps.depts.agents.NEXTSTEPS_AGENT.service import generate_citizen_communication
from apps.depts.agents.department_orchestrator_agent.pydantic_models import (
    DepartmentOrchestratorServiceOutput, ActionPlan, ActionStep, RequestPlan
)
from apps.depts.services.matcher_service import EntityInfo
from apps.depts.services.trigger_orchestrator_service import (
    TriggerOrchestratorOutput, SMSAction, VoiceCallAction, ActionPriority
)
from apps.depts.choices import DepartmentCategory

def create_test_data():
    """Create test data for different emergency scenarios"""

    # Mock Entity Info
    entity_info = EntityInfo(
        id="POL001",
        name="Gulberg Police Station",
        department=DepartmentCategory.POLICE,
        phone="+92-42-35714000",
        address="Main Boulevard, Gulberg III, Lahore",
        city="Lahore",
        coordinates={"lat": 31.5204, "lng": 74.3587},
        distance_km=2.5
    )

    # Mock Department Output - Critical Police Emergency
    critical_action_plan = ActionPlan(
        immediate_actions=[
            ActionStep(
                step_number=1,
                action="Dispatch patrol unit to crime scene immediately",
                timeline="0-5 minutes",
                responsible_party="Police"
            ),
            ActionStep(
                step_number=2,
                action="Contact victim/complainant for detailed statement",
                timeline="5-10 minutes",
                responsible_party="Police"
            )
        ],
        follow_up_actions=[
            ActionStep(
                step_number=1,
                action="File formal complaint and investigation",
                timeline="1-2 hours",
                responsible_party="Police"
            )
        ],
        estimated_resolution_time="Immediate response, investigation ongoing"
    )

    critical_request_plan = RequestPlan(
        incident_summary="House burglary with theft reported",
        location_details="Gulberg area, Lahore - patrol dispatched",
        additional_context="Citizens immediate safety priority, evidence preservation required",
        required_response="Immediate police response and investigation initiation"
    )

    critical_dept_output = DepartmentOrchestratorServiceOutput(
        criticality="critical",
        action_plan=critical_action_plan,
        request_plan=critical_request_plan,
        rationale="Serious crime reported requiring immediate police intervention",
        communication_method="CALL",
        success=True
    )

    # Mock Trigger Output - Critical with Voice Call
    critical_trigger_output = TriggerOrchestratorOutput(
        triggered_actions=[
            VoiceCallAction(
                priority=ActionPriority.IMMEDIATE,
                title="Emergency Voice Alert",
                description="Immediate call to Gulberg Police Station",
                estimated_duration="1-2 minutes",
                recipient_phone="+92-42-35714000",
                call_script="CRITICAL EMERGENCY: House burglary reported in Gulberg area."
            ),
            SMSAction(
                priority=ActionPriority.IMMEDIATE,
                title="Citizen Emergency SMS",
                description="Immediate confirmation to citizen",
                estimated_duration="30 seconds",
                recipient_phone="+92-300-1234567",
                message="🚨 EMERGENCY LOGGED: Police contacted immediately. Stay safe. Help arriving soon."
            )
        ],
        execution_plan="Orchestrated 2 immediate actions for critical emergency",
        total_estimated_time="2 immediate actions, 0 background actions",
        success=True
    )

    return entity_info, critical_dept_output, critical_trigger_output

def test_english_communication():
    """Test English communication"""
    print("🇬🇧 TESTING ENGLISH COMMUNICATION")
    print("=" * 50)

    entity_info, dept_output, trigger_output = create_test_data()

    result = generate_citizen_communication(
        original_request="Someone broke into my house and stole everything",
        department_output=dept_output,
        entity_info=entity_info,
        trigger_output=trigger_output,
        user_phone="+92-300-1234567",
        preferred_language="english"
    )

    if result.success:
        print("✅ SUCCESS!")
        print(f"📱 Message Format: {result.message_format}")
        print(f"🔤 Character Count: {result.character_count}")
        print(f"📞 Reference: {result.reference_number}")

        print(f"\n💬 CITIZEN MESSAGE:")
        print("-" * 30)
        print(result.citizen_message)

        print(f"\n⚡ IMMEDIATE INSTRUCTIONS ({len(result.immediate_instructions)}):")
        for instruction in result.immediate_instructions:
            urgency = "🚨" if instruction.is_urgent else "📋"
            print(f"{urgency} {instruction.step_number}. {instruction.instruction}")
            print(f"   ⏰ Timeline: {instruction.timeline}")

        print(f"\n🔄 WHAT HAPPENS NEXT:")
        print(result.what_happens_next)

        print(f"\n📞 CONTACT INFO:")
        print(f"Primary: {result.contact_info.primary_contact}")
        print(f"Phone: {result.contact_info.phone_number}")
        print(f"Department: {result.contact_info.department_name}")
        if result.contact_info.address:
            print(f"Address: {result.contact_info.address}")

        print(f"\n⏱️ EXPECTED RESPONSE: {result.expected_response_time}")

        if result.safety_reminders:
            print(f"\n🛡️ SAFETY REMINDERS:")
            for reminder in result.safety_reminders:
                print(f"• {reminder}")
    else:
        print(f"❌ FAILED: {result.error_message}")

def test_urdu_communication():
    """Test Urdu communication"""
    print("\n🇵🇰 TESTING URDU COMMUNICATION")
    print("=" * 50)

    entity_info, dept_output, trigger_output = create_test_data()

    result = generate_citizen_communication(
        original_request="میرے گھر میں چوری ہو گئی ہے",
        department_output=dept_output,
        entity_info=entity_info,
        trigger_output=trigger_output,
        user_phone="+92-300-1234567",
        preferred_language="urdu"
    )

    if result.success:
        print("✅ کامیابی!")
        print(f"📱 پیغام کی قسم: {result.message_format}")
        print(f"🔤 حروف کی تعداد: {result.character_count}")
        print(f"📞 ریفرنس: {result.reference_number}")

        print(f"\n💬 شہری کے لیے پیغام:")
        print("-" * 30)
        print(result.citizen_message)

        print(f"\n⚡ فوری ہدایات ({len(result.immediate_instructions)}):")
        for instruction in result.immediate_instructions:
            urgency = "🚨" if instruction.is_urgent else "📋"
            print(f"{urgency} {instruction.step_number}. {instruction.instruction}")
            print(f"   ⏰ وقت: {instruction.timeline}")

        print(f"\n🔄 اگلے اقدامات:")
        print(result.what_happens_next)

        print(f"\n📞 رابطہ کی معلومات:")
        print(f"بنیادی رابطہ: {result.contact_info.primary_contact}")
        print(f"فون: {result.contact_info.phone_number}")
        print(f"شعبہ: {result.contact_info.department_name}")
        if result.contact_info.address:
            print(f"پتہ: {result.contact_info.address}")

        print(f"\n⏱️ متوقع جواب: {result.expected_response_time}")

        if result.safety_reminders:
            print(f"\n🛡️ حفاظتی ہدایات:")
            for reminder in result.safety_reminders:
                print(f"• {reminder}")
    else:
        print(f"❌ ناکام: {result.error_message}")

def test_different_criticality_levels():
    """Test different criticality levels"""
    print("\n📊 TESTING DIFFERENT CRITICALITY LEVELS")
    print("=" * 50)

    entity_info, _, _ = create_test_data()

    criticality_scenarios = [
        {
            "level": "critical",
            "request": "Fire in my building, people trapped",
            "entity": EntityInfo(
                id="FIRE001", name="Rescue 1122", department=DepartmentCategory.FIRE_BRIGADE,
                phone="1122", city="Lahore", distance_km=1.2
            )
        },
        {
            "level": "high",
            "request": "Heart attack, need ambulance urgently",
            "entity": EntityInfo(
                id="AMB001", name="Mayo Hospital", department=DepartmentCategory.AMBULANCE,
                phone="+92-42-99231700", city="Lahore", distance_km=3.1
            )
        },
        {
            "level": "medium",
            "request": "Bank account hacked, money transferred",
            "entity": EntityInfo(
                id="CYB001", name="FIA Cybercrime", department=DepartmentCategory.CYBERCRIME,
                phone="+92-51-9253999", city="Lahore", distance_km=5.0
            )
        }
    ]

    for scenario in criticality_scenarios:
        print(f"\n{scenario['level'].upper()} - {scenario['request'][:40]}...")

        # Create mock department output for this criticality
        mock_dept_output = DepartmentOrchestratorServiceOutput(
            criticality=scenario['level'],
            action_plan=ActionPlan(
                immediate_actions=[ActionStep(1, f"Handle {scenario['level']} emergency", "0-10 minutes", "Department")],
                follow_up_actions=[],
                estimated_resolution_time=f"{scenario['level']} response time"
            ),
            request_plan=RequestPlan(
                incident_summary=scenario['request'],
                location_details="Test location",
                additional_context="Test context",
                required_response=f"{scenario['level']} response"
            ),
            rationale=f"Test {scenario['level']} scenario",
            communication_method="SMS",
            success=True
        )

        mock_trigger_output = TriggerOrchestratorOutput(
            triggered_actions=[],
            execution_plan=f"Test {scenario['level']} execution",
            total_estimated_time="Test time",
            success=True
        )

        result = generate_citizen_communication(
            original_request=scenario['request'],
            department_output=mock_dept_output,
            entity_info=scenario['entity'],
            trigger_output=mock_trigger_output,
            preferred_language="english"
        )

        print(f"Format: {result.message_format} | Chars: {result.character_count}")
        print(f"Entity: {result.contact_info.primary_contact}")
        print(f"Response Time: {result.expected_response_time}")

if __name__ == "__main__":
    try:
        test_english_communication()
        test_urdu_communication()
        test_different_criticality_levels()
        print(f"\n🎉 ALL NEXT-STEPS AGENT TESTS COMPLETED!")

    except Exception as e:
        print(f"💥 TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()