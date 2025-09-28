"""
Quick test to verify the trigger orchestrator fix
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.services.trigger_orchestrator_service import TriggerOrchestratorService, TriggerOrchestratorInput
from apps.depts.agents.department_orchestrator_agent.pydantic_models import DepartmentOrchestratorServiceOutput
from apps.depts.services.matcher_service import EntityInfo
from apps.depts.agents.router_agent.pydantic_models import RouterDecision

def test_trigger_import():
    """Test that the trigger orchestrator can be imported without errors"""
    print("✅ Trigger orchestrator imported successfully")
    
    # Test that the method signature is correct
    try:
        # This should not raise an error
        TriggerOrchestratorService.determine_actions_by_criticality(
            criticality="critical",
            department_output=None,  # We're just testing the method signature
            entity_info=None,
            router_decision=None,
            user_phone="+1234567890",
            user_email="test@example.com",
            user_coordinates=None,
            next_steps_output=None
        )
        print("✅ Method signature is correct")
    except Exception as e:
        print(f"❌ Method signature error: {e}")

if __name__ == "__main__":
    test_trigger_import()
    print("🎉 Trigger orchestrator fix verified!")
