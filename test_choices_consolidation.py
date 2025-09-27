#!/usr/bin/env python
"""
Test script to verify the consolidated choices work correctly
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_choices_consolidation():
    """Test that both Django TextChoices and generated Enum work correctly"""
    
    # Test Django TextChoices
    from apps.depts.choices import DepartmentCategory
    print("✅ Django TextChoices:")
    print(f"   Choices: {DepartmentCategory.choices[:3]}")
    print(f"   Police value: {DepartmentCategory.POLICE}")
    print(f"   Police display: {DepartmentCategory.POLICE.label}")
    
    # Test Generated Enum
    from apps.depts.choices import DepartmentCategoryEnum
    print("\n✅ Generated Enum:")
    print(f"   Enum values: {list(DepartmentCategoryEnum)[:3]}")
    print(f"   Police value: {DepartmentCategoryEnum.POLICE}")
    print(f"   Police display: {DepartmentCategoryEnum.get_display_name('police')}")
    
    # Test that values match
    print("\n✅ Value Consistency:")
    django_values = [choice[0] for choice in DepartmentCategory.choices]
    enum_values = [member.value for member in DepartmentCategoryEnum]
    
    if set(django_values) == set(enum_values):
        print("   ✅ All values match between Django TextChoices and Enum")
    else:
        print("   ❌ Values don't match!")
        print(f"   Django: {django_values}")
        print(f"   Enum: {enum_values}")
    
    # Test imports from other files
    print("\n✅ Import Tests:")
    try:
        from apps.depts.agents.router_agent.choices import DepartmentCategory as RouterAgentCategory
        print("   ✅ Router agent import works")
        print(f"   Router agent Police: {RouterAgentCategory.POLICE}")
    except Exception as e:
        print(f"   ❌ Router agent import failed: {e}")
    
    try:
        from apps.ai_agents.choices.router_agent import DepartmentCategory as AIAgentCategory
        print("   ✅ AI agents import works")
        print(f"   AI agent Police: {AIAgentCategory.POLICE}")
    except Exception as e:
        print(f"   ❌ AI agents import failed: {e}")
    
    try:
        from department_orchestrator_agent.choices import DepartmentCategory as OrchestratorCategory
        print("   ✅ Orchestrator import works")
        print(f"   Orchestrator Police: {OrchestratorCategory.POLICE}")
    except Exception as e:
        print(f"   ❌ Orchestrator import failed: {e}")

if __name__ == "__main__":
    test_choices_consolidation()
