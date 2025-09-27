"""
Department Orchestrator Agent - Middle layer to pick the right specialized agent
"""
from typing import Optional
from agno.agent import Agent
from .prompt import get_department_agent, get_supported_categories

class DepartmentOrchestratorAgent:
    """
    Department Orchestrator Agent - Acts as a picker/router to get the right specialized agent
    This is a middle layer to avoid direct registry usage and provide easy access
    """

    def __init__(self):
        """Initialize the Department Orchestrator Agent"""
        self.supported_categories = get_supported_categories()

    def get_agent_for_category(self, department_category: str) -> Optional[Agent]:
        """
        Get the specialized agent for a given department category

        Args:
            department_category: Department category from router decision

        Returns:
            Agent instance for the department or None if not supported
        """
        if not self.is_category_supported(department_category):
            return None

        return get_department_agent(department_category)

    def is_category_supported(self, department_category: str) -> bool:
        """Check if a department category is supported"""
        return department_category in self.supported_categories

    def get_supported_categories(self) -> list:
        """Get list of all supported department categories"""
        return self.supported_categories.copy()

    def __str__(self):
        return f"DepartmentOrchestratorAgent(supported_categories={len(self.supported_categories)})"

    def __repr__(self):
        return self.__str__()


# Create a singleton instance for easy import
DEPARTMENT_ORCHESTRATOR_AGENT = DepartmentOrchestratorAgent()


# Convenience functions for easy access
def get_specialized_agent(department_category: str) -> Optional[Agent]:
    """
    Convenience function to get specialized agent for a department category

    Args:
        department_category: Department category from router decision

    Returns:
        Agent instance or None if not supported
    """
    return DEPARTMENT_ORCHESTRATOR_AGENT.get_agent_for_category(department_category)


def is_department_supported(department_category: str) -> bool:
    """
    Convenience function to check if department category is supported

    Args:
        department_category: Department category to check

    Returns:
        True if supported, False otherwise
    """
    return DEPARTMENT_ORCHESTRATOR_AGENT.is_category_supported(department_category)