"""
Department Agent Registry - Maps department categories to specialized agents
"""
from typing import Optional
from agno.agent import Agent

def get_department_agent(department_category: str) -> Optional[Agent]:
    """Get the specialized agent for a department category"""

    # Import inside method to avoid circular imports
    from .member_agents.police_agent import POLICE_AGENT
    from .member_agents.fire_agent import FIRE_AGENT
    from .member_agents.ambulance_agent import AMBULANCE_AGENT
    from .member_agents.cybercrime_agent import CYBERCRIME_AGENT
    from .member_agents.disaster_agent import DISASTER_AGENT

    from apps.depts.choices import DepartmentCategory

    agent_mapping = {
        DepartmentCategory.POLICE: POLICE_AGENT,
        DepartmentCategory.FIRE_BRIGADE: FIRE_AGENT,
        DepartmentCategory.AMBULANCE: AMBULANCE_AGENT,
        DepartmentCategory.HEALTH: AMBULANCE_AGENT,  # Health uses ambulance agent
        DepartmentCategory.CYBERCRIME: CYBERCRIME_AGENT,
        DepartmentCategory.DISASTER_MGMT: DISASTER_AGENT,
    }

    return agent_mapping.get(department_category)

def get_supported_categories():
    """Get list of supported department categories"""
    from apps.depts.choices import DepartmentCategory
    return [
        DepartmentCategory.POLICE, DepartmentCategory.FIRE_BRIGADE,
        DepartmentCategory.AMBULANCE, DepartmentCategory.HEALTH,
        DepartmentCategory.CYBERCRIME, DepartmentCategory.DISASTER_MGMT,
        DepartmentCategory.OTHER
    ]