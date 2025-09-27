#!/usr/bin/env python3
"""
Test Trigger Orchestrator Service - Action Orchestration Testing
Tests the TriggerOrchestratorService with different emergency scenarios
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
    trigger_emergency_actions, TriggerOrchestratorService,
    TriggerActionType, ActionPriority
)
from apps.depts.agents.department_orchestrator_agent.pydantic_models import (
    DepartmentOrchestratorServiceOutput, ActionPlan, ActionStep, RequestPlan
)
from apps.depts.services.matcher_service import EntityInfo
from apps.depts.agents.router_agent.pydantic_models import RouterDecision
from apps.depts.choices import DepartmentCategory

def create_test_data():
    """Create comprehensive test data for different scenarios"""

    # Test entities for different departments
    entities = {
        "police": EntityInfo(
            id="POL001",
            name="Gulberg Police Station",
            phone="+92-42-35714000",
            city="Lahore",
            address="Main Boulevard, Gulberg III, Lahore",
            distance_km=2.5,
            match_reason="Closest police station in Gulberg area"
        ),
        "fire": EntityInfo(
            id="FIRE001",
            name="Rescue 1122 - Fire Station",
            phone="1122",
            city="Lahore",
            address="Fire Station Road, Lahore",
            distance_km=1.8,
            match_reason="Nearest fire rescue station"
        ),
        "ambulance": EntityInfo(
            id="AMB001",
            name="Mayo Hospital Emergency",
            phone="+92-42-99231700",
            city="Lahore",
            address="King Edward Medical University Road, Lahore",
            distance_km=3.2,
            match_reason="Major hospital with emergency services"
        ),
        "cyber": EntityInfo(
            id="CYB001",
            name="FIA Cybercrime Circle",
            phone="+92-51-9253999",
            city="Lahore",
            address="FIA Building, Islamabad",
            distance_km=5.0,
            match_reason="Federal cybercrime investigation unit"
        )
    }

    return entities

def create_department_output(criticality: str, department: str, entity_name: str) -> DepartmentOrchestratorServiceOutput:
    """Create mock department output for different scenarios"""

    scenarios = {
        "critical": {
            "action_plan": ActionPlan(
                immediate_actions=[
                    ActionStep(1, "Dispatch emergency response team immediately", "0-3 minutes", "Department"),
                    ActionStep(2, "Secure the area and establish perimeter", "3-10 minutes", "Department"),
                    ActionStep(3, "Initiate emergency medical support if needed", "5-15 minutes", "Department")
                ],
                follow_up_actions=[
                    ActionStep(1, "Complete incident documentation", "30-60 minutes", "Department"),
                    ActionStep(2, "Coordinate with additional agencies if required", "1-2 hours", "Department")
                ],
                estimated_resolution_time="Immediate response - 15-30 minutes initial, ongoing investigation"
            ),
            "request_plan": RequestPlan(
                incident_summary=f"Critical emergency requiring immediate {department} response",
                location_details="Emergency location identified - immediate dispatch authorized",
                additional_context="High priority incident with potential safety risks",
                required_response="Immediate multi-channel emergency response with backup coordination"
            )
        },
        "high": {
            "action_plan": ActionPlan(
                immediate_actions=[
                    ActionStep(1, f"Notify {department} duty officer immediately", "0-5 minutes", "Department"),
                    ActionStep(2, "Prepare response team and equipment", "5-15 minutes", "Department")
                ],
                follow_up_actions=[
                    ActionStep(1, "Conduct detailed assessment", "15-30 minutes", "Department"),
                    ActionStep(2, "Implement appropriate response measures", "30-60 minutes", "Department")
                ],
                estimated_resolution_time="Urgent response - 30-45 minutes"
            ),
            "request_plan": RequestPlan(
                incident_summary=f"High priority {department} matter requiring urgent attention",
                location_details="Location verified - urgent response team deployment",
                additional_context="Significant incident requiring prompt departmental action",
                required_response="Urgent response with priority handling and follow-up"
            )
        },
        "medium": {
            "action_plan": ActionPlan(
                immediate_actions=[
                    ActionStep(1, f"Log incident in {department} system", "0-10 minutes", "Department"),
                    ActionStep(2, "Schedule appropriate response", "10-30 minutes", "Department")
                ],
                follow_up_actions=[
                    ActionStep(1, "Conduct investigation or inspection", "1-3 hours", "Department"),
                    ActionStep(2, "Provide resolution or recommendations", "3-6 hours", "Department")
                ],
                estimated_resolution_time="Scheduled response - 2-4 hours"
            ),
            "request_plan": RequestPlan(
                incident_summary=f"Medium priority {department} service request",
                location_details="Location noted - scheduled response planned",
                additional_context="Standard service request requiring departmental attention",
                required_response="Scheduled response with detailed communication"
            )
        },
        "low": {
            "action_plan": ActionPlan(
                immediate_actions=[
                    ActionStep(1, f"Record request in {department} queue", "0-15 minutes", "Department")
                ],
                follow_up_actions=[
                    ActionStep(1, "Review request during next business cycle", "24-48 hours", "Department"),
                    ActionStep(2, "Provide information or guidance", "48-72 hours", "Department")
                ],
                estimated_resolution_time="Standard processing - 24-48 hours"
            ),
            "request_plan": RequestPlan(
                incident_summary=f"Low priority {department} information request",
                location_details="Location noted for reference",
                additional_context="Standard information or service inquiry",
                required_response="Standard communication and information provision"
            )
        }
    }

    scenario_data = scenarios.get(criticality, scenarios["medium"])

    return DepartmentOrchestratorServiceOutput(
        criticality=criticality,
        action_plan=scenario_data["action_plan"],
        request_plan=scenario_data["request_plan"],
        rationale=f"Determined as {criticality} priority based on incident analysis",
        communication_method="CALL" if criticality == "critical" else ("SMS" if criticality == "high" else "EMAIL"),
        success=True
    )

def create_router_decision(department: DepartmentCategory) -> RouterDecision:
    """Create mock router decision"""
    return RouterDecision(
        department=department,
        confidence=0.9,
        urgency_indicators=["emergency", "urgent"],
        reason=f"Request classified as {department.value} matter",
        keywords_detected=["emergency", "help", "urgent"],
        degraded_mode_used=False,
        classification_source="llm"
    )

def test_critical_scenarios():
    """Test CRITICAL emergency scenarios with maximum actions"""
    print("🚨 TESTING CRITICAL EMERGENCY SCENARIOS")
    print("=" * 60)

    entities = create_test_data()

    critical_scenarios = [
        {
            "name": "Critical Police Emergency - Armed Robbery",
            "entity": entities["police"],
            "department": DepartmentCategory.POLICE,
            "request": "Armed men robbed my shop and threatened customers",
            "user_phone": "+92-300-1234567",
            "user_email": "citizen@example.com",
            "coordinates": {"lat": 31.5204, "lng": 74.3587}
        },
        {
            "name": "Critical Fire Emergency - Building Fire",
            "entity": entities["fire"],
            "department": DepartmentCategory.FIRE_BRIGADE,
            "request": "Building on fire with people trapped inside",
            "user_phone": "+92-301-9876543",
            "coordinates": {"lat": 31.5580, "lng": 74.3507}
        },
        {
            "name": "Critical Medical Emergency - Heart Attack",
            "entity": entities["ambulance"],
            "department": DepartmentCategory.AMBULANCE,
            "request": "Person having heart attack, needs immediate medical help",
            "user_phone": "+92-302-5555555",
            "coordinates": {"lat": 31.5656, "lng": 74.3141}
        }
    ]

    for i, scenario in enumerate(critical_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 50)
        print(f"📞 Request: {scenario['request']}")
        print(f"🏢 Entity: {scenario['entity'].name}")
        print(f"📱 User Phone: {scenario.get('user_phone', 'Not provided')}")

        try:
            # Create test data
            dept_output = create_department_output("critical", scenario['department'].value, scenario['entity'].name)
            router_decision = create_router_decision(scenario['department'])

            # Test the trigger orchestrator
            result = trigger_emergency_actions(
                department_output=dept_output,
                entity_info=scenario['entity'],
                router_decision=router_decision,
                user_phone=scenario.get('user_phone'),
                user_email=scenario.get('user_email'),
                user_coordinates=scenario.get('coordinates')
            )

            if result.success:
                print(f"✅ SUCCESS - {len(result.triggered_actions)} actions orchestrated")
                print(f"📋 Plan: {result.execution_plan}")
                print(f"⏱️ Time: {result.total_estimated_time}")

                print(f"\n🎯 TRIGGERED ACTIONS:")
                for j, action in enumerate(result.triggered_actions, 1):
                    print(f"  {j}. {action.title} ({action.action_type.value})")
                    print(f"     🚨 Priority: {action.priority.value}")
                    print(f"     📝 {action.description}")
                    print(f"     ⏰ Duration: {action.estimated_duration}")

                    # Show specific action details
                    if action.action_type == TriggerActionType.VOICE_CALL:
                        print(f"     📞 Calling: {action.recipient_phone}")
                        print(f"     💬 Script: {action.call_script[:50]}...")
                    elif action.action_type == TriggerActionType.SMS:
                        print(f"     📱 SMS to: {action.recipient_phone}")
                        print(f"     💬 Message: {action.message[:50]}...")
                    elif action.action_type == TriggerActionType.NEARBY_SEARCH:
                        print(f"     🔍 Search: {action.search_query}")
                        print(f"     📍 Radius: {action.radius_km}km")

            else:
                print(f"❌ FAILED: {result.error_message}")

        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")

def test_all_priority_levels():
    """Test all priority levels with different action combinations"""
    print(f"\n\n📊 TESTING ALL PRIORITY LEVELS")
    print("=" * 60)

    entities = create_test_data()
    police_entity = entities["police"]
    router_decision = create_router_decision(DepartmentCategory.POLICE)

    priority_levels = ["critical", "high", "medium", "low"]

    for priority in priority_levels:
        print(f"\n🎯 TESTING {priority.upper()} PRIORITY")
        print("-" * 40)

        try:
            dept_output = create_department_output(priority, "Police", police_entity.name)

            result = trigger_emergency_actions(
                department_output=dept_output,
                entity_info=police_entity,
                router_decision=router_decision,
                user_phone="+92-300-1234567",
                user_email="test@example.com",
                user_coordinates={"lat": 31.5204, "lng": 74.3587}
            )

            if result.success:
                print(f"✅ Actions: {len(result.triggered_actions)}")

                # Count actions by priority
                priority_counts = {}
                for action in result.triggered_actions:
                    p = action.priority.value
                    priority_counts[p] = priority_counts.get(p, 0) + 1

                print(f"📊 Priority Distribution:")
                for p, count in priority_counts.items():
                    print(f"   • {p}: {count} actions")

                print(f"🎯 Action Types:")
                for action in result.triggered_actions:
                    print(f"   • {action.action_type.value} ({action.priority.value})")

            else:
                print(f"❌ FAILED: {result.error_message}")

        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print(f"\n\n🔍 TESTING EDGE CASES")
    print("=" * 60)

    entities = create_test_data()
    police_entity = entities["police"]
    router_decision = create_router_decision(DepartmentCategory.POLICE)

    edge_cases = [
        {
            "name": "No User Phone or Email",
            "user_phone": None,
            "user_email": None,
            "coordinates": None
        },
        {
            "name": "No Entity Phone",
            "entity_phone": None,
            "user_phone": "+92-300-1234567"
        },
        {
            "name": "Invalid Coordinates",
            "coordinates": {"lat": 999, "lng": 999},
            "user_phone": "+92-300-1234567"
        }
    ]

    for i, case in enumerate(edge_cases, 1):
        print(f"\n{i}. {case['name']}")
        print("-" * 30)

        try:
            # Modify entity for specific test cases
            test_entity = police_entity
            if case.get("entity_phone") is None:
                test_entity = EntityInfo(
                    id=police_entity.id,
                    name=police_entity.name,
                    phone=None,  # No phone
                    city=police_entity.city,
                    address=police_entity.address,
                    distance_km=police_entity.distance_km,
                    match_reason="Test entity with no phone"
                )

            dept_output = create_department_output("critical", "Police", test_entity.name)

            result = trigger_emergency_actions(
                department_output=dept_output,
                entity_info=test_entity,
                router_decision=router_decision,
                user_phone=case.get("user_phone"),
                user_email=case.get("user_email"),
                user_coordinates=case.get("coordinates")
            )

            if result.success:
                print(f"✅ Handled gracefully - {len(result.triggered_actions)} actions")
                for action in result.triggered_actions:
                    print(f"   • {action.action_type.value}")
            else:
                print(f"⚠️ Limited functionality: {result.error_message}")

        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")

def interactive_menu():
    """Interactive menu for testing trigger orchestrator"""

    print("\n" + "="*60)
    print("🎯 TRIGGER ORCHESTRATOR TESTING MENU")
    print("="*60)
    print("1. Test Critical Emergency Scenarios")
    print("2. Test All Priority Levels (Critical → Low)")
    print("3. Test Edge Cases & Error Handling")
    print("4. Test Individual Critical Scenario")
    print("5. Test Individual Priority Level")
    print("6. Run All Tests")
    print("0. Exit")
    print("-" * 40)

    while True:
        try:
            choice = input("\nSelect test to run (0-6): ").strip()

            if choice == "1":
                test_critical_scenarios()
            elif choice == "2":
                test_all_priority_levels()
            elif choice == "3":
                test_edge_cases()
            elif choice == "4":
                test_individual_critical_scenario()
            elif choice == "5":
                test_individual_priority_level()
            elif choice == "6":
                test_critical_scenarios()
                test_all_priority_levels()
                test_edge_cases()
            elif choice == "0":
                print("\n👋 Testing complete. Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 0-6.")

            input("\nPress Enter to return to menu...")

        except KeyboardInterrupt:
            print("\n\n👋 Testing interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Error: {e}")

def test_individual_critical_scenario():
    """Test individual critical scenarios with manual selection"""
    print("\n🚨 SELECT CRITICAL SCENARIO TO TEST")
    print("=" * 50)

    entities = create_test_data()
    critical_scenarios = [
        {
            "name": "Critical Police Emergency - Armed Robbery",
            "entity": entities["police"],
            "department": DepartmentCategory.POLICE,
            "request": "Armed men robbed my shop and threatened customers",
            "user_phone": "+92-300-1234567",
            "user_email": "citizen@example.com",
            "coordinates": {"lat": 31.5204, "lng": 74.3587}
        },
        {
            "name": "Critical Fire Emergency - Building Fire",
            "entity": entities["fire"],
            "department": DepartmentCategory.FIRE_BRIGADE,
            "request": "Building on fire with people trapped inside",
            "user_phone": "+92-301-9876543",
            "coordinates": {"lat": 31.5580, "lng": 74.3507}
        },
        {
            "name": "Critical Medical Emergency - Heart Attack",
            "entity": entities["ambulance"],
            "department": DepartmentCategory.AMBULANCE,
            "request": "Person having heart attack, needs immediate medical help",
            "user_phone": "+92-302-5555555",
            "coordinates": {"lat": 31.5656, "lng": 74.3141}
        }
    ]

    print("Available scenarios:")
    for i, scenario in enumerate(critical_scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Request: {scenario['request'][:50]}...")

    try:
        choice = int(input("\nSelect scenario (1-3): ")) - 1
        if 0 <= choice < len(critical_scenarios):
            scenario = critical_scenarios[choice]

            print(f"\n🎯 Testing: {scenario['name']}")
            print("=" * 50)
            print(f"📞 Request: {scenario['request']}")
            print(f"🏢 Entity: {scenario['entity'].name}")
            print(f"📱 User Phone: {scenario.get('user_phone', 'Not provided')}")

            # Create test data
            dept_output = create_department_output("critical", scenario['department'].value, scenario['entity'].name)
            router_decision = create_router_decision(scenario['department'])

            # Test the trigger orchestrator
            result = trigger_emergency_actions(
                department_output=dept_output,
                entity_info=scenario['entity'],
                router_decision=router_decision,
                user_phone=scenario.get('user_phone'),
                user_email=scenario.get('user_email'),
                user_coordinates=scenario.get('coordinates')
            )

            if result.success:
                print(f"\n✅ SUCCESS - {len(result.triggered_actions)} actions orchestrated")
                print(f"📋 Plan: {result.execution_plan}")
                print(f"⏱️ Time: {result.total_estimated_time}")

                print(f"\n🎯 TRIGGERED ACTIONS:")
                for j, action in enumerate(result.triggered_actions, 1):
                    print(f"  {j}. {action.title} ({action.action_type.value})")
                    print(f"     🚨 Priority: {action.priority.value}")
                    print(f"     📝 {action.description}")
                    print(f"     ⏰ Duration: {action.estimated_duration}")

                    # Show specific action details
                    if action.action_type == TriggerActionType.VOICE_CALL:
                        print(f"     📞 Calling: {action.recipient_phone}")
                        print(f"     💬 Script: {action.call_script[:50]}...")
                    elif action.action_type == TriggerActionType.SMS:
                        print(f"     📱 SMS to: {action.recipient_phone}")
                        print(f"     💬 Message: {action.message[:50]}...")
                    elif action.action_type == TriggerActionType.NEARBY_SEARCH:
                        print(f"     🔍 Search: {action.search_query}")
                        print(f"     📍 Radius: {action.radius_km}km")

            else:
                print(f"❌ FAILED: {result.error_message}")

        else:
            print("❌ Invalid scenario selection.")
    except ValueError:
        print("❌ Please enter a valid number.")
    except Exception as e:
        print(f"💥 Error: {e}")

def test_individual_priority_level():
    """Test individual priority levels with manual selection"""
    print("\n📊 SELECT PRIORITY LEVEL TO TEST")
    print("=" * 50)

    priority_levels = ["critical", "high", "medium", "low"]

    print("Available priority levels:")
    for i, priority in enumerate(priority_levels, 1):
        print(f"{i}. {priority.upper()} Priority")

    try:
        choice = int(input("\nSelect priority level (1-4): ")) - 1
        if 0 <= choice < len(priority_levels):
            priority = priority_levels[choice]

            print(f"\n🎯 Testing: {priority.upper()} PRIORITY")
            print("=" * 50)

            entities = create_test_data()
            police_entity = entities["police"]
            router_decision = create_router_decision(DepartmentCategory.POLICE)

            dept_output = create_department_output(priority, "Police", police_entity.name)

            result = trigger_emergency_actions(
                department_output=dept_output,
                entity_info=police_entity,
                router_decision=router_decision,
                user_phone="+92-300-1234567",
                user_email="test@example.com",
                user_coordinates={"lat": 31.5204, "lng": 74.3587}
            )

            if result.success:
                print(f"✅ Actions Generated: {len(result.triggered_actions)}")

                # Count actions by priority
                priority_counts = {}
                for action in result.triggered_actions:
                    p = action.priority.value
                    priority_counts[p] = priority_counts.get(p, 0) + 1

                print(f"\n📊 Priority Distribution:")
                for p, count in priority_counts.items():
                    print(f"   • {p}: {count} actions")

                print(f"\n🎯 Action Types Generated:")
                for action in result.triggered_actions:
                    print(f"   • {action.action_type.value} ({action.priority.value})")
                    print(f"     Title: {action.title}")
                    print(f"     Description: {action.description}")

            else:
                print(f"❌ FAILED: {result.error_message}")

        else:
            print("❌ Invalid priority selection.")
    except ValueError:
        print("❌ Please enter a valid number.")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Trigger Orchestrator Testing...")
    print("This will test the TriggerOrchestratorService with different emergency scenarios.")
    print("Choose individual tests or run the complete suite.")

    interactive_menu()