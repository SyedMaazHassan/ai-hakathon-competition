from apps.depts.agents.department_agent.member_agents.police_agent import POLICE_AGENT
from apps.depts.agents.department_agent.member_agents.hospital_agent import HOSPITAL_AGENT
from apps.depts.agents.department_agent.member_agents.fire_brigade import FIRE_AGENT
from apps.depts.agents.department_agent.member_agents.electricity_agent import ELECTRICITY_AGENT
from apps.depts.agents.department_agent.member_agents.general_support_agent import GENERAL_SUPPORT_AGENT
from apps.depts.choices import DepartmentCategoryEnum
from apps.depts.helper import PromptTemplate

class PromptRegistry:
    """Registry of all domain-specific AI prompts."""

    POLICE_AGENT = POLICE_AGENT
    HOSPITAL_AGENT = HOSPITAL_AGENT
    FIRE_AGENT = FIRE_AGENT
    ELECTRICITY_AGENT = ELECTRICITY_AGENT
    GENERAL_SUPPORT_AGENT = GENERAL_SUPPORT_AGENT

    # Registry map
    _DEPARTMENT_MAP = {
        DepartmentCategoryEnum.POLICE: POLICE_AGENT,
        # DepartmentCategoryEnum.HOSPITAL: HOSPITAL_AGENT,
        DepartmentCategoryEnum.FIRE_BRIGADE: FIRE_AGENT,
        # DepartmentCategoryEnum.ELECTRICITY: ELECTRICITY_AGENT,
        # DepartmentCategoryEnum.GENERAL_SUPPORT: GENERAL_SUPPORT_AGENT,
    }

    @classmethod
    def get_prompt(cls, department: DepartmentCategoryEnum) -> PromptTemplate:
        """Return the correct PromptTemplate for a given department key."""
        return cls._DEPARTMENT_MAP.get(department, cls.GENERAL_SUPPORT_AGENT)
